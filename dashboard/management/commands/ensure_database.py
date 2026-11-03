import pymysql
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Create the configured MySQL database if it does not exist (no-op for SQLite)."""

    help = 'Create the MySQL database named in DB_NAME if it is missing.'
    requires_system_checks = []  # model checks connect to the (possibly missing) database

    def handle(self, *args, **options):
        db = settings.DATABASES['default']
        if 'mysql' not in db['ENGINE']:
            self.stdout.write(f"  Using SQLite: {db['NAME']}")
            return

        try:
            conn = pymysql.connect(host=db['HOST'], port=int(db['PORT'] or 3306),
                                   user=db['USER'], password=db['PASSWORD'], charset='utf8mb4')
        except pymysql.MySQLError as e:
            raise CommandError(f'Could not connect to MySQL at {db["HOST"]}:{db["PORT"]}: {e}')

        name = db['NAME'].replace('`', '')
        with conn, conn.cursor() as cur:
            cur.execute(f'CREATE DATABASE IF NOT EXISTS `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        self.stdout.write(f'  MySQL database `{name}` is ready.')
