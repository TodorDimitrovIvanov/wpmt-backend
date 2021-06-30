import json

# Source: https://www.sqlitetutorial.net/sqlite-python/
import sqlite3
from sqlite3 import Error


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
        # TODO: Add error handling and reporting
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
        # TODO: Add error handling and reporting
        db_conn = DB.db_conn_start(db_file)
        db_cursor = db_conn.cursor()
        db_cursor.execute(sql_command)
        temp = db_cursor.fetchall()
        db_conn.close()
        return temp

    ###################
    ###### USERS ######
    @staticmethod
    def db_user_login(db_file, email, client_key):
        sql_prep = "SELECT * FROM users WHERE email=? AND client_key=?"
        sql_data = [email, client_key]
        db_conn = DB.db_conn_start(db_file)
        db_cur = db_conn.cursor()
        db_cur.execute(sql_prep, sql_data)
        result = db_cur.fetchall()
        db_conn.close()
        return result


    @staticmethod
    def db_user_add(db_file, client_id, client_key, email, name, service, notifications, icon):
        sql_prep = "INSERT INTO users (client_id, client_key, email, name, service, notifications, icon) VALUES (?,?,?,?,?,?,?);"
        sql_data = [client_id, client_key, email, name, service, notifications, icon]
        # TODO: Add error handling and reporting
        db_conn = DB.db_conn_start(db_file)
        db_cur = db_conn.cursor()
        db_cur.execute(sql_prep, sql_data)
        db_conn.commit()
        db_conn.close()

    @staticmethod
    def db_user_get(db_file, client_key, email):
        sql_prep = "SELECT * FROM users WHERE client_key=? AND email=?"
        sql_data = [client_key, email]
        db_conn = DB.db_conn_start(db_file)
        db_cur = db_conn.cursor()
        db_cur.execute(sql_prep, sql_data)
        result = db_cur.fetchall()
        db_conn.close()
        return result

    @staticmethod
    def db_user_all(db_file):
        # Here prepare the SQL request and gather the data
        sql_prep = "SELECT * FROM users"
        db_conn = DB.db_conn_start(db_file)
        db_cur = db_conn.cursor()
        db_cur.execute(sql_prep)
        columns = list(map(lambda x: x[0], db_cur.description))
        data = db_cur.fetchall()

        # Here we transform the data into JSON format
        temp_dict = {}
        result = {}
        for entry in range(len(data)):
            for index in range(len(columns)):
                item = data[entry]
                key = columns[index]
                temp_dict[key] = item[index]
            result[entry] = json.dumps(temp_dict, indent=4, separators=('\n', ','))
        # The "result" is a dictionary of dictionaries.
        # Each dictionary contains the keys and values from the "users" table
        return result
    ###### USERS ######
    ###################


    #####################
    ###### WEBSITE ######
    @staticmethod
    def db_site_add(db_file, website_id, client_id, domain, dom_exp, certificate, cert_exp):
        sql_prep = "INSERT INTO website (website_id, client_id, domain, domain_expiry, certificate, certificate_expiry) VALUES (?,?,?,?,?,?);"
        sql_data = [website_id, client_id, domain, dom_exp, certificate, cert_exp]
        # TODO: Add error handling and reporting
        db_conn = DB.db_conn_start(db_file)
        db_cur = db_conn.cursor()
        db_cur.execute(sql_prep, sql_data)
        db_conn.commit()
        db_conn.close()

    @staticmethod
    def db_site_get(db_file, client_id, domain):
        sql_prep = "SELECT * FROM website WHERE client_id=? AND domain=?"
        sql_data = [client_id, domain]
        # TODO: Add error handling and reporting
        db_conn = DB.db_conn_start(db_file)
        db_cur = db_conn.cursor()
        db_cur.execute(sql_prep, sql_data)
        result = db_cur.fetchall()
        db_conn.close()
        return result

    @staticmethod
    def db_site_all(db_file, client_id):
        # Here prepare the SQL request and gather the data
        sql_prep = "SELECT * FROM website"
        db_conn = DB.db_conn_start(db_file)
        db_cur = db_conn.cursor()
        db_cur.execute(sql_prep)
        columns = list(map(lambda x: x[0], db_cur.description))
        data = db_cur.fetchall()

        # Here we transform the data into JSON format
        temp_dict = {}
        result = {}
        for entry in range(len(data)):
            for index in range(len(columns)):
                item = data[entry]
                key = columns[index]
                temp_dict[key] = item[index]
            result[entry] = json.dumps(temp_dict, indent=4, separators=('\n', ','))
        # The "result" is a dictionary of dictionaries.
        # Each dictionary contains the keys and values from the "website" table
        return result

    @staticmethod
    def db_site_user(db_file, client_id):
        sql_prep = "SELECT * FROM website WHERE client_id=?"
        sql_data = [client_id]
        db_conn = DB.db_conn_start(db_file)
        db_cur = db_conn.cursor()
        db_cur.execute(sql_prep, sql_data)
        result = db_cur.fetchall()
        db_conn.close()
        return result
    ###### WEBSITE ######
    #####################
