# mysql_patch.py
import pymysql

# Override the version to satisfy Django's requirement
pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.__version__ = "2.2.1"

# Install as MySQLdb
pymysql.install_as_MySQLdb()