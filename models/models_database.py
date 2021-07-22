import json
# Source: https://www.sqlitetutorial.net/sqlite-python/
import sqlite3
from typing import Optional
from fastapi import HTTPException
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
    def request_data(db_file, request: str, data: Optional[list] = None):
        try:
            # Source: https://stackoverflow.com/questions/32372353/how-to-create-a-db-file-in-sqlite3-using-a-schema-file-from-within-python
            # Docs: https://docs.python.org/2/library/sqlite3.html#sqlite3.Cursor.executescript
            db_conn = DB.db_conn_start(db_file)
            db_cur = db_conn.cursor()
            if data is None:
                print("SQL Query: ", request)
                result = db_cur.execute(request)
                if result is not None:
                    temp = result.fetchall()
                    db_conn.close()
                    return temp
                else:
                    raise TypeError
            else:
                result = db_cur.execute(request, data)

                if result is not None:
                    temp = result.fetchall()
                    db_conn.close()
                    return temp
                else:
                    raise TypeError
        except sqlite3.Error as e:
            message = "[Local][DB][Error][02]: Couldn't connect to DB. \nRequest: " + request + "\nFull error message: " + str(e)
            router.send_to_logger("error", message, client_id=None, client_email=None)
            raise HTTPException(
                status_code=500,
                detail=message
            )
        except OSError as e:
            message = "[Local][DB][Error][01]: Couldn't open DB. \nRequest: " + request + "\nFull error message: " + str(e)
            router.send_to_logger("error", message, client_id=None, client_email=None)
            raise HTTPException(
                status_code=500,
                detail=message
            )
        except TypeError as e:
            message = "[Local][DB][Error][03]: Received None as a response from the DB. \nRequest: " + request + "\nFull error message: " + str(e)
            router.send_to_logger("error", message, client_id=None, client_email=None)
            raise HTTPException(
                status_code=500,
                detail=message
            )


    @staticmethod
    def insert_data(db_file, request: str, data: Optional[list] = None):
        try:
            # Source: https://stackoverflow.com/questions/32372353/how-to-create-a-db-file-in-sqlite3-using-a-schema-file-from-within-python
            # Docs: https://docs.python.org/2/library/sqlite3.html#sqlite3.Cursor.executescript
            db_conn = DB.db_conn_start(db_file)
            db_cur = db_conn.cursor()
            if data is None:
                db_cur.execute(request)
                db_conn.commit()
                return True
            else:
                db_cur.execute(request, data)
                db_conn.commit()
                return True
        except sqlite3.Error as e:
            message = "[Local][DB][Error][02]: Couldn't connect to DB. \nRequest: " + request + "\nFull error message: " + str(e)
            router.send_to_logger("error", message, client_id=None, client_email=None)
            raise HTTPException(
                status_code=500,
                detail=message
            )
            return False
        except OSError as e:
            message = "[Local][DB][Error][01]: Couldn't open DB. \nRequest: " + request + "\nFull error message: " + str(e)
            router.send_to_logger("error", message, client_id=None, client_email=None)
            raise HTTPException(
                status_code=500,
                detail=message
            )
            return False
        except TypeError as e:
            message = "[Local][DB][Error][03]: Received None as a response from the DB. \nRequest: " + request + "\nFull error message: " + str(e)
            router.send_to_logger("error", message, client_id=None, client_email=None)
            raise HTTPException(
                status_code=500,
                detail=message
            )
            return False


    @staticmethod
    def init(db_source, db_file):
        try:
            with open(db_source, 'r') as sql_file:
                sql_command = sql_file.read()
            db_conn = DB.db_conn_start(db_file)
            cursor = db_conn.cursor()
            cursor.executescript(sql_command)
            db_conn.close()
        except sqlite3.Error as e:
            message = "[Local][DB][Error][02]: Couldn't connect to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message, client_id=None, client_email=None)
            raise HTTPException(
                status_code=500,
                detail=message
            )
        except OSError as e:
            message = "[Local][DB][Error][01]: Couldn't opem to DB. \nFull error message: " + str(e)
            router.send_to_logger("error", message, client_id=None, client_email=None)
            raise HTTPException(
                status_code=500,
                detail=message
            )

    @staticmethod
    def db_state_save(db_file, website_id, data):
        pass

    @staticmethod
    def db_state_compare(db_file, website_id):
        pass

    @staticmethod
    def db_struct_list(db_file):
        # Source: https://stackoverflow.com/questions/305378/list-of-tables-db-schema-dump-etc-using-the-python-sqlite3-api
        sql_command = "SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';"
        # First we send a request to the DB
        # Note error handling is managed by the request_data function
        temp = DB.request_data(db_file, sql_command)
        # Here we transform the results into a json-like object
        temp_dict = {}
        for index, item in enumerate(temp):
            temp_dict["table" + str(index + 1)] = item[0]
        # And then we return the transformed json object
        return temp_dict

    ###################
    ###### USERS ######
    @staticmethod
    def db_user_login(db_file, email, client_key):
        sql_command = "SELECT * FROM users WHERE email=? AND client_key=?"
        sql_data = [email, client_key]
        temp = DB.request_data(db_file, sql_command, sql_data)
        return temp

    @staticmethod
    def db_user_add(db_file, client_id, client_key, email, name, service, notifications, promos):
        sql_command = "INSERT INTO users (client_id, client_key, email, name, service, notifications, promos) VALUES (?,?,?,?,?,?,?);"
        sql_data = [client_id, client_key, email, name, service, notifications, promos]
        temp = DB.insert_data(db_file, sql_command, data=sql_data)
        if temp:
            return True
        else:
            return False

    @staticmethod
    def db_user_get(db_file, client_key, email):
        sql_command = "SELECT * FROM users WHERE client_key=? AND email=?"
        sql_data = [client_key, email]
        temp = DB.request_data(db_file, sql_command, sql_data)
        if len(temp) >= 1:
            # Here we transform the results into a json-like object
            temp_dict = {
                "client_id": temp[0][0],
                "client_key": temp[0][1],
                "email": temp[0][2],
                "name": temp[0][3],
                "service": temp[0][4],
                "notifications": temp[0][5],
                "promos": temp[0][6]
            }
            return temp_dict
        else:
            return {
                "Response": "Not Found"
            }

    @staticmethod
    def db_user_session(db_file, client_email):
        # Here prepare the SQL request and gather the data
        sql_command = "SELECT client_id,  service, notifications, promos FROM users WHERE email=?"
        sql_data = [client_email]
        temp = DB.request_data(db_file, sql_command, sql_data)
        result_dict = {
            "client_id": temp[0][0],
            "service": temp[0][1],
            "notifications": temp[0][2],
            "promos": temp[0][3]
        }
        return result_dict

    @staticmethod
    def db_user_all(db_file):
        # Here prepare the SQL request and gather the data
        sql_prep = "SELECT * FROM users"
        temp = DB.request_data(db_file, sql_prep)
        result_dict = {}
        for index, entry in enumerate(temp):
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


    @staticmethod
    def db_user_export(db_file, client_id, website_id):
        # Here we retrieve the available websites
        sql_command = "SELECT users.client_id, website.website_id, website.domain FROM users " \
                      "INNER JOIN website ON website.client_id = users.client_id WHERE users.client_id = ?"
        sql_data = [client_id]
        temp = DB.request_data(db_file, sql_command, sql_data)
        print("DB User Export: ", temp)

        sql_command2 = "SELECT website.website_id, accounts.account_id, accounts.hostname, " \
                       "accounts.username, accounts.password, accounts.port, accounts.path FROM website " \
                       "INNER JOIN website ON website.website_id = accounts.website_id WHERE website.website_id = ?"
        sql_data2 = [website_id]
        temp2 = DB.request_data(db_file, sql_command2, sql_data2)
        print("DB User Export: ", temp2)

        # TODO: Complete the export functionality by merging temp and temp2 into a dictionary
        result_dict = {}
        return result_dict

    ###### USERS ######
    ###################

    #####################
    ###### WEBSITE ######
    @staticmethod
    def db_site_add(db_file, website_id, client_id, domain, dom_exp, certificate, cert_exp):
        sql_command = "INSERT INTO website (website_id, client_id, domain, domain_expiry, certificate, certificate_expiry) VALUES (?,?,?,?,?,?);"
        sql_data = [website_id, client_id, domain, dom_exp, certificate, cert_exp]
        temp = DB.insert_data(db_file, sql_command, sql_data)
        if temp:
            return True
        else:
            return False

    @staticmethod
    def db_site_get(db_file, client_id, domain):
        sql_command = "SELECT * FROM website WHERE client_id=? AND domain=?"
        sql_data = [client_id, domain]
        temp = DB.request_data(db_file, sql_command, sql_data)
        temp_dict = {
            "site_id": temp[0][0],
            "client_id": temp[0][1],
            "domain": temp[0][2],
            "domain_exp": temp[0][3],
            "certificate": temp[0][4],
            "cert_exp": temp[0][5]
        }
        return temp_dict


    @staticmethod
    def db_site_count_get(db_file, client_id):
        sql_prep = "SELECT COUNT(*) FROM website WHERE client_id=?"
        sql_data = [client_id]
        temp = DB.request_data(db_file, sql_prep, sql_data)
        return temp[0][0]

    @staticmethod
    def db_site_all(db_file):
        # Here prepare the SQL request and gather the data
        sql_command = "SELECT * FROM website"
        temp = DB.request_data(db_file, sql_command, data=None)
        result_dict = {}
        for index, entry in enumerate(temp):
            temp_dict = {
                "website_id": entry[0],
                "client_id": entry[1],
                "domain": entry[2],
                "domain_exp": entry[3],
                "certificate": entry[4],
                "cert_exp": entry[5]
            }
            result_dict[index] = temp_dict
        return result_dict

    @staticmethod
    def db_site_user(db_file, client_id):
        sql_command = "SELECT * FROM website WHERE client_id=?"
        sql_data = [client_id]
        temp = DB.request_data(db_file, sql_command, sql_data)
        result_dict = {}
        for index, entry in enumerate(temp):
            temp_dict = {
                "website_id": entry[0],
                "client_id": entry[1],
                "domain": entry[2],
                "domain_exp": entry[3],
                "certificate": entry[4],
                "cert_exp": entry[5]
            }
            result_dict[index] = temp_dict
        return result_dict
    ###### WEBSITE ######
    #####################

    #####################
    ###### ACCOUNTS #####
    @staticmethod
    def account_add(db_file, account_id: str, website_id: str, acc_type: str, hostname: str, username:str, password: str, port: int, path: Optional[str]= "/"):
        sql_command = "INSERT INTO accounts (account_id, website_id, type, hostname, username, password, port, path) VALUES (?,?,?,?,?,?,?);"
        sql_data = [account_id, website_id, acc_type, hostname, username, password, port, path]
        temp = DB.insert_data(db_file, sql_command, sql_data)
        if temp:
            return True
        else:
            return False

    @staticmethod
    def accounts_type_get(db_file, website_id, acc_type):
        sql_command = "SELECT * FROM accounts WHERE website_id=? AND type=? "
        sql_data = [website_id, acc_type]
        temp = DB.request_data(db_file, sql_command, sql_data)
        result_dict = {}
        for index, entry in enumerate(temp):
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

    @staticmethod
    def account_count(db_file, website_id: str):
        sql_command = "SELECT COUNT(*) FROM accounts WHERE website_id=?"
        sql_data = [website_id]
        temp = DB.request_data(db_file, sql_command, sql_data)
        if temp is not None:
            return temp[0][0]


    @staticmethod
    def account_delete(db_file, client_id, account_id: str):
        sql_command = "DELETE FROM accounts WHERE account_id=? and website_id=?"
        sql_data = [account_id, client_id]
        # Don't mind the 'insert_data' function name here. It uses the "db_conn.commit()" method
        # Which is used for inserting and deleting data from the DB and returns boolean
        # Based on the outcome of the SQL command
        temp = DB.insert_data(db_file, sql_command, sql_data)
        if temp:
            return True
        else:
            return False
    ###### ACCOUNTS #####
    #####################