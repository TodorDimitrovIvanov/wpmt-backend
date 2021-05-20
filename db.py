import sqlite3
from sqlite3 import Error
# Source: https://www.sqlitetutorial.net/sqlite-python/


class DB:

    @staticmethod
    def db_conn_start(db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as err:
            print("ERROR: Couldn't connect to wpmt.db")
        finally:
            return conn

    @staticmethod
    def db_init(db_source, db_file):
        sql_command = None
        with open(db_source, 'r') as sql_file:
            sql_command = sql_file.read()
        db_conn = DB.db_conn_start(db_file)
        cursor = db_conn.cursor()
        # Source: https://stackoverflow.com/questions/32372353/how-to-create-a-db-file-in-sqlite3-using-a-schema-file-from-within-python
        # Docs: https://docs.python.org/2/library/sqlite3.html#sqlite3.Cursor.executescript
        cursor.executescript(sql_command)
        db_conn.close()

    @staticmethod
    def db_struct_list(db_file):
        # Source: https://stackoverflow.com/questions/305378/list-of-tables-db-schema-dump-etc-using-the-python-sqlite3-api
        sql_command = "SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';"
        db_conn = DB.db_conn_start(db_file)
        db_cursor = db_conn.cursor()
        db_cursor.execute(sql_command)
        print(db_cursor.fetchall())
        db_conn.close()

    @staticmethod
    def db_add_user(db_file, client_id, client_key, email, name, service, notifications, icon):
        pass