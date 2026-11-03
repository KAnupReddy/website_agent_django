"""
Copy all data from the original CodeIgniter 4 MySQL database into this app.

    python manage.py import_legacy                       # reads LEGACY_DB_* from .env
    python manage.py import_legacy --db autobiz_ai --user root

Rows keep their original IDs. Existing rows with the same ID are updated.
Built designs are re-written into this project's writable/builds folder so
previews and ZIP downloads work without the old PHP install.
"""

import pymysql
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from dashboard.models import Business, Deployment, Design, Email, Enrichment
from dashboard.services.utils import build_dir_for

# (model, legacy table, legacy FK column → Django field)
TABLES = [
    (Business, 'restaurants', {}),
    (Enrichment, 'enrichments', {'restaurant_id': 'business_id'}),
    (Design, 'designs', {'restaurant_id': 'business_id'}),
    (Deployment, 'deployments', {}),
    (Email, 'emails', {'restaurant_id': 'business_id'}),
]


class Command(BaseCommand):
    help = 'Import businesses, enrichments, designs, deployments and emails from the CI4 database.'

    def add_arguments(self, parser):
        env = settings.LEGACY_DB
        parser.add_argument('--host', default=env['HOST'])
        parser.add_argument('--port', type=int, default=env['PORT'])
        parser.add_argument('--db', default=env['NAME'])
        parser.add_argument('--user', default=env['USER'])
        parser.add_argument('--password', default=env['PASSWORD'])

    def handle(self, *args, **opts):
        try:
            conn = pymysql.connect(host=opts['host'], port=opts['port'], user=opts['user'],
                                   password=opts['password'], database=opts['db'],
                                   charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        except pymysql.MySQLError as e:
            raise CommandError(f'Could not connect to legacy database: {e}')

        with conn, transaction.atomic():
            for model, table, renames in TABLES:
                fields = {f.attname for f in model._meta.concrete_fields}
                with conn.cursor() as cur:
                    cur.execute(f'SELECT * FROM `{table}`')
                    rows = cur.fetchall()

                for row in rows:
                    data = {renames.get(k, k): v for k, v in row.items()}
                    data = {k: v for k, v in data.items() if k in fields}
                    for key in ('created_at', 'updated_at', 'deployed_at', 'sent_at'):
                        if data.get(key) and timezone.is_naive(data[key]):
                            data[key] = timezone.make_aware(data[key])
                    pk = data.pop('id')
                    model.objects.update_or_create(id=pk, defaults=data)
                    # auto_now / auto_now_add overwrite timestamps on save — restore the originals
                    model.objects.filter(id=pk).update(created_at=data.get('created_at'), updated_at=data.get('updated_at'))

                self.stdout.write(f'  {table:<12} -> {model.__name__:<10} {len(rows)} rows')

            rebuilt = self._rebuild_design_files()
            self.stdout.write(f'  rebuilt {rebuilt} design files in {settings.BUILD_DIR}')

        self.stdout.write(self.style.SUCCESS('Import complete.'))

    @staticmethod
    def _rebuild_design_files():
        count = 0
        designs = Design.objects.select_related('business').exclude(html_code__isnull=True).exclude(html_code='')
        for design in designs.exclude(status=Design.Status.DRAFT):
            out_dir = build_dir_for(design.business.name)
            out_dir.mkdir(parents=True, exist_ok=True)
            path = out_dir / design.filename
            path.write_text(design.html_code, encoding='utf-8')
            Design.objects.filter(id=design.id).update(preview_path=str(path))
            count += 1
        return count
