import json
# Source: https://www.sqlitetutorial.net/sqlite-python/
import sqlite3
import router


class DB:

    @staticmethod
    def db_conn_start(db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except sqlite3.Error as err:
            print("ERROR: Couldn't connect to wpmt.db")
        finally:
            return conn

    @staticmethod
    def db_init(db_source, db_file):
        try:
            with open(db_source, 'r') as sql_file:
                sql_command = sql_file.read()
            db_conn = DB.db_conn_start(db_file)
            cursor = db_conn.cursor()
            # Source: https://stackoverflow.com/questions/32372353/how-to-create-a-db-file-in-sqlite3-using-a-schema-file-from-within-python
            # Docs: https://docs.python.org/2/library/sqlite3.html#sqlite3.Cursor.executescript
            cursor.executescript(sql_command)
            db_conn.close()
        except sqlite3.Error as e:
            message = "[Local][DB][Error][02]: Couldn't connect to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message)
        except OSError as e:
            message = "[Local][DB][Error][01]: Couldn't opem to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message)

    @staticmethod
    def db_struct_list(db_file):
        # Source: https://stackoverflow.com/questions/305378/list-of-tables-db-schema-dump-etc-using-the-python-sqlite3-api
        sql_command = "SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';"
        try:
            db_conn = DB.db_conn_start(db_file)
            db_cursor = db_conn.cursor()
            db_cursor.execute(sql_command)
            temp = db_cursor.fetchall()
            db_conn.close()
            # Here we transform the results into a json-like object
            temp_dict = {}
            for index, item in enumerate(temp):
                temp_dict["table" + str(index + 1)] = item[0]
            print(temp_dict)
            return temp_dict
        except sqlite3.Error as e:
            message = "[Local][DB][Error][02]: Couldn't connect to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message)
        except OSError as e:
            message = "[Local][DB][Error][01]: Couldn't opem to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message)

    ###################
    ###### USERS ######
    @staticmethod
    def db_user_login(db_file, email, client_key):
        sql_prep = "SELECT * FROM users WHERE email=? AND client_key=?"
        try:
            sql_data = [email, client_key]
            db_conn = DB.db_conn_start(db_file)
            db_cur = db_conn.cursor()
            db_cur.execute(sql_prep, sql_data)
            result = db_cur.fetchall()
            db_conn.close()
            return result
        except sqlite3.Error as e:
            message = "[Local][DB][Error][02]: Couldn't connect to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message)
        except OSError as e:
            message = "[Local][DB][Error][01]: Couldn't opem to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message)

    @staticmethod
    def db_user_add(db_file, client_id, client_key, email, name, service, notifications, promos):
        sql_prep = "INSERT INTO users (client_id, client_key, email, name, service, notifications, promos) VALUES (?,?,?,?,?,?,?);"
        try:
            sql_data = [client_id, client_key, email, name, service, notifications, promos]
            db_conn = DB.db_conn_start(db_file)
            db_cur = db_conn.cursor()
            db_cur.execute(sql_prep, sql_data)
            db_conn.commit()
            db_conn.close()
            return True
        except sqlite3.Error as e:
            message = "[Local][DB][Error][02]: Couldn't connect to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message)
        except OSError as e:
            message = "[Local][DB][Error][01]: Couldn't opem to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message)

    @staticmethod
    def db_user_get(db_file, client_key, email):
        sql_prep = "SELECT * FROM users WHERE client_key=? AND email=?"
        try:
            sql_data = [client_key, email]
            db_conn = DB.db_conn_start(db_file)
            db_cur = db_conn.cursor()
            db_cur.execute(sql_prep, sql_data)
            result = db_cur.fetchall()
            db_conn.close()
            # Here we transform the results into a json-like object
            temp_dict = {
                "client_id": result[0][0],
                "client_key": result[0][1],
                "email": result[0][2],
                "name": result[0][3],
                "service": result[0][4],
                "notifications": result[0][5],
                "promos": result[0][6]
            }
            return temp_dict
        except sqlite3.Error as e:
            message = "[Local][DB][Error][02]: Couldn't connect to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message)
        except OSError as e:
            message = "[Local][DB][Error][01]: Couldn't opem to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message)

    @staticmethod
    def db_user_session(db_file, client_email):
        # Here prepare the SQL request and gather the data
        sql_prep = "SELECT client_id,  service, notifications, promos FROM users WHERE email=?"
        try:
            sql_data = [client_email]
            db_conn = DB.db_conn_start(db_file)
            db_cur = db_conn.cursor()
            db_cur.execute(sql_prep, sql_data)
            result = db_cur.fetchall()

            result_dict = {
                "client_id": result[0],
                "service": result[1],
                "notifications": result[2],
                "promos": result[3]
            }
            return result_dict
        except sqlite3.Error as e:
            message = "[Local][DB][Error][02]: Couldn't connect to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message)
        except OSError as e:
            message = "[Local][DB][Error][01]: Couldn't opem to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message)


    @staticmethod
    def db_user_all(db_file):
        # Here prepare the SQL request and gather the data
        sql_prep = "SELECT * FROM users"
        try:
            db_conn = DB.db_conn_start(db_file)
            db_cur = db_conn.cursor()
            db_cur.execute(sql_prep)
            result = db_cur.fetchall()
            result_dict = {}
            for index, entry in enumerate(result):
                temp_dict = {
                    "client_id": entry[0],
                    "client_key": entry[1],
                    "email": entry[2],
                    "name": entry[3],
                    "service": entry[4],
                    "notifications": entry[5],
                    "promos": entry[6]
                }
                result_dict[index] = temp_dict
            return result_dict
        except sqlite3.Error as e:
            message = "[Local][DB][Error][02]: Couldn't connect to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message)
        except OSError as e:
            message = "[Local][DB][Error][01]: Couldn't opem to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message)


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


def db_user_all():
    return None