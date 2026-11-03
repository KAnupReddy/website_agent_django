import logging

from ..models import Business, Design
from .utils import build_dir_for

logger = logging.getLogger('autobiz')


class BuildAgent:
    """Saves draft HTML designs to the local filesystem as preview files."""

    def build(self, business_id: int) -> list[str]:
        """Write all draft designs for a business to disk; return the file paths."""
        business = Business.objects.filter(pk=business_id).first()
        if not business:
            return []

        designs = list(Design.objects.filter(business=business, status=Design.Status.DRAFT))
        if not designs:
            logger.warning('[BuildAgent] No draft designs for business #%s', business_id)
            return []

        out_dir = build_dir_for(business.name)
        out_dir.mkdir(parents=True, exist_ok=True)

        paths = []
        for design in designs:
            path = out_dir / design.filename
            path.write_text(design.html_code or '', encoding='utf-8')

            design.preview_path = str(path)
            design.status = Design.Status.BUILT
            design.save(update_fields=['preview_path', 'status', 'updated_at'])

            paths.append(str(path))
            logger.info('[BuildAgent] Written: %s', path)

        return paths
