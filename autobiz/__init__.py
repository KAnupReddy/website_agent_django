import pymysql

# PyMySQL stands in for mysqlclient (no C compiler needed on Windows).
# Django checks the mysqlclient version, so report a compatible one.
pymysql.version_info = (2, 2, 1, 'final', 0)
pymysql.__version__ = '2.2.1'
pymysql.install_as_MySQLdb()
