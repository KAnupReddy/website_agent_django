import ftplib
import logging
import os
import posixpath

from django.conf import settings
from django.utils import timezone

from ..models import Business, Deployment, Design
from .utils import slugify

logger = logging.getLogger('autobiz')


class HostingAgent:
    """Deploys built website files to a remote server via FTP and creates live demo URLs."""

    def __init__(self):
        cfg = settings.HOSTING
        self.ftp_host = cfg['FTP_HOST']
        self.ftp_user = cfg['FTP_USER']
        self.ftp_pass = cfg['FTP_PASS']
        self.ftp_root = (cfg['FTP_ROOT'] or '/public_html/demos/').rstrip('/') + '/'
        self.base_domain = cfg['BASE_DOMAIN'] or 'localhost'

    def deploy(self, business_id: int) -> list[str]:
        """Deploy all built designs for a business and return their live URLs."""
        business = Business.objects.filter(pk=business_id).first()
        if not business:
            return []

        designs = list(Design.objects.filter(business=business, status=Design.Status.BUILT))
        if not designs:
            logger.warning('[HostingAgent] No built designs for business #%s', business_id)
            return []

        slug = slugify(business.name)
        urls = []

        for design in designs:
            if not design.preview_path or not os.path.exists(design.preview_path):
                logger.warning('[HostingAgent] Missing file for design #%s', design.id)
                continue

            remote_path = f'{self.ftp_root}{slug}/{design.filename}'
            url = f'https://demos.{self.base_domain}/{slug}/{design.filename}'

            deployment = Deployment.objects.create(
                design=design,
                url=url,
                subdomain=f'demos.{self.base_domain}',
                ftp_path=remote_path,
                status=Deployment.Status.PENDING,
            )

            if self._upload_via_ftp(design.preview_path, remote_path, deployment):
                urls.append(url)
                design.status = Design.Status.DEPLOYED
                design.save(update_fields=['status', 'updated_at'])

        if urls:
            business.status = Business.Status.DEPLOYED
            business.save(update_fields=['status', 'updated_at'])

        return urls

    def _upload_via_ftp(self, local_path: str, remote_path: str, deployment: Deployment) -> bool:
        if not self.ftp_host:
            # No FTP configured — simulate success for local dev
            logger.info('[HostingAgent] FTP not configured. Simulating upload of %s', local_path)
            self._mark_live(deployment)
            return True

        try:
            with ftplib.FTP(self.ftp_host, timeout=60) as ftp:
                ftp.login(self.ftp_user, self.ftp_pass)
                ftp.set_pasv(True)
                self._mkdir_recursive(ftp, posixpath.dirname(remote_path))
                with open(local_path, 'rb') as fh:
                    ftp.storbinary(f'STOR {remote_path}', fh)
        except ftplib.error_perm as e:
            self._record_error(deployment, f'FTP error for {remote_path}: {e}')
            return False
        except (OSError, ftplib.Error) as e:
            self._record_error(deployment, f'Could not connect to FTP host {self.ftp_host}: {e}')
            return False

        self._mark_live(deployment)
        logger.info('[HostingAgent] Uploaded: %s', remote_path)
        return True

    @staticmethod
    def _mkdir_recursive(ftp: ftplib.FTP, remote_dir: str) -> None:
        path = ''
        for part in remote_dir.strip('/').split('/'):
            path += '/' + part
            try:
                ftp.cwd(path)
            except ftplib.error_perm:
                ftp.mkd(path)
        ftp.cwd('/')

    @staticmethod
    def _mark_live(deployment: Deployment) -> None:
        deployment.status = Deployment.Status.LIVE
        deployment.deployed_at = timezone.now()
        deployment.save(update_fields=['status', 'deployed_at', 'updated_at'])

    @staticmethod
    def _record_error(deployment: Deployment, msg: str) -> None:
        logger.error('[HostingAgent] %s', msg)
        deployment.status = Deployment.Status.FAILED
        deployment.error_msg = msg
        deployment.save(update_fields=['status', 'error_msg', 'updated_at'])
