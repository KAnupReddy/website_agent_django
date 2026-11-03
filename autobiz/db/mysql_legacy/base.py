"""
MySQL backend that accepts older servers (e.g. XAMPP's MariaDB 10.4).

Django 6 refuses to connect to MariaDB < 10.11 / MySQL < 8.4 and assumes
features those versions added. This backend lowers the minimum to MariaDB 10.4 /
MySQL 8.0 and turns off the features older MariaDB releases lack. Use it for
local development; prefer an upgraded server in production.
"""

from django.db.backends.mysql import base, features
from django.utils.functional import cached_property


class DatabaseFeatures(features.DatabaseFeatures):
    @property
    def minimum_database_version(self):
        return (10, 4) if self.connection.mysql_is_mariadb else (8, 0)

    def _mariadb_at_least(self, version):
        return self.connection.mysql_is_mariadb and self.connection.mysql_version >= version

    @cached_property
    def can_return_columns_from_insert(self):
        return self._mariadb_at_least((10, 5))  # INSERT … RETURNING

    @cached_property
    def has_native_uuid_field(self):
        return self._mariadb_at_least((10, 7))  # UUID column type

    @cached_property
    def can_rename_index(self):
        return not self.connection.mysql_is_mariadb or self._mariadb_at_least((10, 5, 2))


class DatabaseWrapper(base.DatabaseWrapper):
    features_class = DatabaseFeatures
