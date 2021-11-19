from json import JSONDecodeError

from fastapi import FastAPI, HTTPException, Request
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import requests
import json
import uuid
import sched, time, datetime


# Custom modules
from models import models_file, models_post, models_database, models_connection
# These are POST body models that the API endpoints expect to receive
# This is an  ASGI (Asynchronous Server Gateway Interface) server on which the API runs
# Source: https://www.uvicorn.org/
import uvicorn
from os.path import expanduser


# -------------------------
# Temporary code
# When live the API should be able to retrieve the DB settings (and others) from the config.json file

app = FastAPI()
global user_session

user_home = expanduser("~")
db_source = "./dbs/wpmt-v1.4.sql"
db_file = user_home + "/WPMT/db/wpmt.db"
app_home = user_home + "/WPMT"

# -------------------------
__cluster_name__ = "cluster-eu01.wpmt.org"
__cluster_url__ = "http://cluster-eu01.wpmt.org"
__cluster_logger_url__ = "http://cluster-eu01.wpmt.org/log/save"
__cluster_locale__ = "EU"
# -------------------------

# -------------------------
__wpmt_php_client_url__ = ""
__app_headers__ = {
    'Host': 'cluster-eu01.wpmt.org',
    'User-Agent': 'WPMT-Client-API/1.0',
    'Referer': 'http://localhost:13337/router.py',
    'Content-Type': 'application/json'
}

# -------------------------
# Daemon-like module for executing tasks at regular intervals
# It will be used for syncing the state of the App DB
scheduler = sched.scheduler(time.time, time.sleep)
# -------------------------


# -------------------------
# START of SYSTEM section
# -------------------------

#   --------------------
#   START of State Class
#   --------------------
class State:

    @staticmethod
    def state_local_generate():
        # Here we directly use the "user_session" global variable
        # As using the "session_get()" function returns the following error:
        # 'staticmethod' object is not callable
        global user_session
        if user_session is None:
            return {
                "Response": "Error",
                "Message": "Not Allowed"
            }
        else:
            website_states = models_database.DB.db_user_export_websites(db_file, user_session['client_id'])
            wordpress_states = {}
            backup_states = {}
            notification_states = {}
            temp_time = datetime.datetime.utcnow()
            now = temp_time.strftime("%b-%d-%Y-%H:%M")
            if None not in [website_states, wordpress_states, backup_states, notification_states]:
                result_dict = {
                    "client_id": user_session['client_id'],
                    "last_update": now,
                    "session_id": user_session['session_id'],
                    "client_ip": user_session['client_ip'],
                    "website_states": website_states,
                    "wordpress_states": wordpress_states,
                    "backup_states": backup_states,
                    "notification_states": notification_states
                }
            else:
                return {
                    "Response": "Error",
                    "Message": "One of the states is not set!"
                }
        return result_dict

    @staticmethod
    def state_local_get():
        current_session = session_get()
        if current_session is None:
            return {
                "Response": "Error",
                "Message": "Not Allowed"
            }
        else:
            result = models_database.DB.db_user_state_get(db_file, current_session['client_id'])
            return result

    @staticmethod
    def state_local_set(state_obj: dict):
        current_session = session_get()
        if current_session is None:
            return {
                "Response": "Error",
                "Message": "Not Allowed"
            }
        else:
            if state_obj is not None:
                result = models_database.DB.db_user_state_set(db_file, state_obj)
                if result:
                    return {
                        "Response": "Success",
                        "Message": "State saved successfully"
                    }
                else:
                    return {
                        "Response": "Error",
                        "Message": "State not saved"
                    }

    @staticmethod
    def state_cluster_get():
        current_session = session_get()
        if current_session is None:
            return {
                "Response": "Error",
                "Message": "Not Allowed"
            }
        else:
            url = __cluster_url__ + "/state/get"
            result = requests.post(url, json={"client_id": current_session['client_id']})
            if result:
                current_cluster_state = result.json()
                temp = State.state_local_get()
                current_local_state = json.loads(temp[0][0])
                cluster_update = datetime.datetime.strptime(current_cluster_state['last_update'], '%b-%d-%Y-%H:%M')
                local_update = datetime.datetime.strptime(current_local_state['last_update'], '%b-%d-%Y-%H:%M')
                # Here we check if the State on the Cluster is older
                if cluster_update < local_update:
                    # If the State is older:
                    # TODO: We're here in the development process
                    # Here we need to send a POST request to the Cluster and provide the local state
                    # So the State on the server can be updated
                    url2 = __cluster_url__ + "/state/set"
                    json_data = {}
                    json_data['state_obj'] = current_local_state
                    result2 = requests.post(url2, json=json_data)
                    if result2:
                        return result2.json()
                    else:
                        message = "The State for user [" + current_session['client_id'] + "] was not properly set on the Cluster"
                        return{
                            "Response": "Failure",
                            "Message": message
                        }
                else:
                    result = State.state_local_set(current_cluster_state)
                    result["Info"] = "Changed the local State"
                    return result
            else:
                return {
                    "Response": "Error",
                    "Message": "No state found for the [" + current_session['client_id'] + "] user"
                }
#   --------------------
#   END of State Class
#   --------------------


#   --------------------
#   START of Session Class
#   --------------------
class Session:

    @staticmethod
    def session_create(email, client_ip, client_os):
        if email is not None and email != "":
            try:
                db_query = models_database.DB.db_user_session(db_file, email)
                session_obj = {
                    "session_id": str(uuid.uuid1()),
                    "client_id": db_query['client_id'],
                    "client_ip": client_ip,
                    "client_os": client_os,
                    "email": email,
                    "service": db_query['service'],
                    "active_website": "",
                    "notifications": db_query['notifications'],
                    "promos": db_query['promos']
                }
                # Code below may be deprecated depending on how user sessions will be managed
                # Either with files or in memory. With the current setup it will managed in memory
                '''session_file = router.app_home + '/' + 'session'
                with open(session_file, 'a') as session_opened:
                    json.dump(session_obj, session_opened)'''
                return session_obj
            except OSError as e:
                message = "[Client][Session][Error][01]: Couldn't create session file. Full error message: " + str(e)
                send_to_logger("error", message, db_query[0])

    @staticmethod
    def session_invalidate(session_obj):
        session_obj = None
#   --------------------
#   END of Session Class
#   --------------------


@app.get("/")
def read_root():
    if models_file.db_setup() and models_file.config_setup():
        return {"Response: Success"}
    else:
        return {"Response: Failure"}


# Functions below are to be removed once development is completed
# They provide utility for debugging the App and are a major security risk
@app.get("/db/structure", status_code=200)
def db_struct_get():
    result = models_database.DB.db_struct_list(db_file)
    return result


@app.get("/db/init", status_code=200)
def db_init():
    models_database.DB.init(db_source, db_file)
    return {
        "Response": "DB Initialized"
    }


@app.post("/db/list", status_code=200)
def db_list(post_data: models_post.DBSearch):
    post_data_dict = post_data.dict()
    result = models_database.DB.db_table_list(db_file, post_data_dict['table_name'])
    return result


def session_get():
    try:
        global user_session
        if user_session is not None:
            return user_session
        else:
            return HTTPException(
                status_code=403,
                detail="Not Allowed"
            )
    except NameError as e:
        message = "[Client][API][Error][02]: This protected request lacks authentication."
        print(message)


def send_to_logger(err_type, message):
    global __app_headers__
    global user_session
    if user_session is None:
        print("User session not defined or something...")
    else:
        # TODO: Remove the parameters once its verified that the user_session is properly received
        #print("Send to Logger Debug. Client_id: ", user_session['client_id'], user_session['email'])
        body = {
            "client_id": user_session['client_id'],
            "client_email": user_session['email'],
            "type": err_type,
            "message": message
        }
        send_request = requests.post(__cluster_logger_url__, data=json.dumps(body), headers=__app_headers__)
# -------------------------
# END of SYSTEM section
# -------------------------


# -------------------------
# START of USER Section
# -------------------------
@app.post("/user/add")
async def user_add(user: models_post.User):
    result_dic = user.dict()

    send_request = requests.post(__cluster_url__ + "/user/add", data=json.dumps(result_dic), headers=__app_headers__)
    response = (send_request.content).decode()
    response_dict = json.loads(response)
    if response_dict['Response'] == "Error":
        raise HTTPException(
            status_code=500,
            detail=response_dict['Message']
        )
    else:
        if models_database.DB.db_user_add(db_file, response_dict['client_id'], response_dict['client_key'],
                                          result_dic['email'], result_dic['name'], result_dic['service'],
                                          result_dic['notifications'], result_dic['promos']):
            return {
                "Response": "Success",
                "client_id": response_dict['client_id'],
                "client_key": response_dict['client_key']
            }
        else:
            raise HTTPException(
                error_code=500,
                detail="Random Error Message")


@app.post("/user/get", status_code=200)
def user_get(search: models_post.UserSearch):
    result_dic = search.dict()
    result = models_database.DB.db_user_get(db_file, result_dic['client_key'], result_dic['email'])
    # If such user exists
    if len(result) >= 1:
        return result
    # If such user doesn't exist
    else:
        return {
            "Response": "Not Found"
        }


@app.get("/user/all", status_code=200)
def user_all():
    result = models_database.DB.db_user_all(db_file)
    # If there are any registered users
    if len(result) >= 1:
        return result
    # If there are no registered user
    else:
        return {
            "Response": "No users found"
        }


@app.post("/user/login")
async def login(login_model: models_post.UserLogin, request: Request):
    # Source: https://jordanisaacs.github.io/fastapi-sessions/guide/getting_started/
    result_dic = login_model.dict()

    # Source: https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/#encryption
    # Here we encrypt the client's email address using the public key the client provides
    try:
        key_raw = result_dic['client_key'].replace('\\n', '\n')
        key_encoded = key_raw.encode()
        public_key_obj = load_pem_public_key(
            key_encoded,
            default_backend())
        encrypted_message = public_key_obj.encrypt(
            result_dic['email'].encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None)
        )
        # Then pass the bot the non/encrypted email to the WPMT Cluster API
        # There the WPMT Cluster API retrieves the user's private key and decrypts the encrypted address
        # If the decrypted email address matches what's stored in the WPMT Cluster DB the API returns a 200 OK
        body = {
            "email": result_dic['email'],
            "encrypted_email": encrypted_message.hex()
        }
        send_request = requests.post(__cluster_url__ + "/auth/verify", data=json.dumps(body), headers=__app_headers__)

        response = json.loads(send_request.content)
        # scheduler.enter(600, 1, db_sync())
        if response['Response'] == "Success":
            import platform
            client_ip = request.client.host
            temp_sess = Session.session_create(result_dic['email'], client_ip, platform.system())
            # Here we set the global variable to the newly created object
            global user_session
            user_session = temp_sess
            return {
                "Response": "Success"
            }
        else:
            raise HTTPException(
                status_code=403,
                detail="Failed Authentication"
            )
    except JSONDecodeError:
        # Here we retrieve the client's IP address using the FastApi 'Request' class
        # Source: https://fastapi.tiangolo.com/advanced/using-request-directly/#use-the-request-object-directly
        message = "[Client][API][Error][02]: Received an error from the Cluster API. Most likely failed authentication."
        print("Message: ", message)
        send_to_logger("error", message, client_id=None, client_email=result_dic['email'])
        return {
            "Response": "Error",
            "Message": "Failed authentication attempt. Double-check email and public key. "
        }
    except ValueError as err:
        message = "[Client][API][Error][01]: The provided key is malformed and can't be loaded. Full Error: " + str(err)
        print("Message: ", message)
        send_to_logger("error", message, client_id=None, client_email=result_dic['email'])
        return {
            "Response": "Error",
            "Message": "The provided key is corrupted or not in the correct format."
        }


@app.get("/user/logout")
async def logout():
    global user_session
    user_session = None


@app.get("/user/state/sync")
async def sync():
    global user_session
    if user_session is None:
        raise HTTPException(statuscode=403)
        return
    else:
        result = State.state_cluster_get()
        return result


@app.get("/user/state/get", status_code=200)
async def state_get():
    try:
        global user_session
        if user_session is None:
            raise HTTPException(
                status_code=403,
                detail="Not Allowed")
        else:
            # TODO: We're up to here for the moment
            # We need to add a post model for checking the state on the Cluster
            # And it should have the client_id within it
            temp = State.state_local_get()
            #print("DEBUG: Router.state_get.DICT: ", temp[0][0])
            if temp is None:
                return{
                    "Response": "Failure",
                    "Message": "No State found"
                }
            else:
                result = json.loads(temp[0][0])
                return result
    except NameError as err:
        raise HTTPException(
            status_code=403,
            detail="[Client][API][Error][03]: Error Message: " + str(err))


@app.get("/user/state/set", status_code=200)
async def state_set():
    global user_session
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed")
    else:
        temp = State.state_local_generate()
        #print("DEBUG: Router.state_set.DICT: ", temp)
        result = State.state_local_set(temp)
        if result:
            return {
                "Response": "Success",
                "State": temp
            }
        else:
            return {
                "Response": "Failure",
                "Message": "The state was not properly saved within the DB"
            }
# -------------------------
# END of USER section
# -------------------------


# -------------------------
# START of WEBSITE section
# -------------------------
@app.post("/website/add", status_code=200)
# Here we check whether the user has logged in before we allow him to add a website
# This is done via the "session_data" parameter
def website_add(website: models_post.Website):
    try:
        current_session = session_get()
        if current_session is None:
            raise HTTPException(statuscode=403)
        else:
            result_dic = website.dict()
            # Here we generate the ID of the website
            new_site_num = int(models_database.DB.db_site_count_get(db_file, current_session['client_id']))
            website_id = current_session['client_id'] + ":SITE-" + str(new_site_num + 1).zfill(4)

            if models_database.DB.db_site_add(db_file, website_id, current_session['client_id'], result_dic['domain'],
                                           result_dic['domain_exp'], result_dic['certificate'], result_dic['certificate_exp']):
                current_session['active_website'] = website_id
                return {
                    "Response": "Success",
                    "domain": result_dic['domain'],
                    "website_id": website_id,
                    "client_id": current_session['client_id']
                }
            else:
                return {
                    "Response": "Error",
                    "Message": "[Cluster][DB][03]: Failed adding data to DB"
                }
    except NameError:
        return HTTPException(status_code=403)


@app.post("/website/get", status_code=200)
def website_get(search: models_post.WebsiteSearch):
    try:
        global user_session
        if user_session is None:
            raise HTTPException(status_code=403)
        else:
            result_dic = search.dict()
            result = models_database.DB.db_site_get(db_file, user_session['client_id'], result_dic['domain'])
            return result
    except NameError:
        return HTTPException(status_code=403)


@app.post('/website/get/id', status_code=200)
def website_get_id(search: models_post.WebsiteID):
    try:
        global user_session
        if user_session is None:
            raise HTTPException(status_code=403)
        else:
            result_dic = search.dict()
            result = models_database.DB.db_site_get_id(db_file, result_dic['website_id'])
            return result
    except NameError:
        return HTTPException(status_code=403)


# Note: This function should be removed as it could pose a security risk
# It's currently used for debugging purposes
@app.get("/website/all", status_code=200)
def website_all():
    result = models_database.DB.db_site_all(db_file)
    return result


@app.post("/website/user", status_code=200)
async def website_user():
    try:
        global user_session
        if user_session is not None:
            print(user_session['client_id'])
            result = models_database.DB.db_site_user(db_file, user_session['client_id'])
            return result
        else:
            raise HTTPException(status_code=403)
    except NameError:
        return HTTPException(status_code=403)


@app.post("/website/active/set")
async def website_active_set(post_data: models_post.WebsiteID):
    post_data_dict = post_data.dict()
    global user_session
    if user_session is not None:
        sql_result = models_database.DB.db_site_get(db_file, user_session['client_id'], post_data_dict['website_id'])
        user_session['active_website'] = sql_result['website_id']
        return {
            "Response": "Success",
        }
    else:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )


@app.get("/website/active/get")
async def website_active_get():
    global user_session
    if user_session is not None:
        if user_session['active_website'] != "":
            return user_session
        else:
            return {
                "Response": "Error",
                "Message": "There's no website currently active"
            }
    else:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )

# -------------------------
# END of WEBSITE section
# -------------------------


# -------------------------
# START of ACCOUNTS section
# -------------------------
@app.post("/website/account/add", status_code=200)
async def account_add(post_data: models_post.Account):
    current_session = session_get()
    if current_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed")
    else:
        if current_session['active_website'] == "" or None:
            return{
                "Response": "Error",
                "Message": "The Session is missing an 'active_website'."
            }
        else:
            # Here we retrieve the the data provided from the POST request
            post_data_dict = post_data.dict()
            # Here we generate the ID of the account that's being added
            last_account_id = models_database.DB.account_count(db_file, current_session['active_website'])
            account_id = current_session['active_website'] + ":ACC-" + str(last_account_id + 1).zfill(4)

            result = models_database.DB.account_add(db_file, account_id,
                                                    current_session['active_website'], post_data_dict['type'],
                                                    post_data_dict['hostname'], post_data_dict['username'],
                                                    post_data_dict['password'], post_data_dict['port'],
                                                    post_data_dict['path'])
            if result:
                return {
                    "Response": "Success",
                    "account_id": account_id
                }
            else:
                return {
                    "Response": "Error",
                    "Message": "No records found!"
                }



@app.post("/website/account/type/get", status_code=200)
async def account_type_get(post_data: models_post.AccountTypeGet):
    # This function will return all accounts of certain type (SSH,FTP, etc.) for the specified website
    global user_session
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_data.dict()
        current_session = session_get()
        result = models_database.DB.accounts_type_get(db_file, current_session['active_website'], post_data_dict['account_type'])
        if result:
            return result
        else:
            return {
                "Response": "Error",
                "Message": "No records found!"
            }


@app.post("/website/account/all", status_code=200)
async def account_all():
    current_session = session_get()
    if current_session is None or current_session['active_website'] == "":
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
        return
    else:
        result = models_database.DB.accounts_all(db_file, current_session['active_website'])
        if result:
            return result
        else:
            return {
                "Response": "Error",
                "Message": "No records found!"
            }


@app.post("/website/account/get", status_code=200)
async def account_get(post_data: models_post.AccountGet):
    current_session = session_get()
    if current_session is None or current_session['active_website'] == "":
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
        return
    else:
        post_data_dict = post_data.dict()
        result = models_database.DB.account_get(db_file, user_session['active_website'], post_data_dict['account_id'])
        if result:
            return {
                "Response": "Success",
                "account": result
            }
        else:
            return{
                "Response": "Failure",
                "Message": "Account not found"
            }


@app.post("/website/account/delete", status_code=200)
async def account_delete(post_data: models_post.AccountGet):
    # This function expects to receive the account_id after the user is logged in and selects an account to be deleted.
    global user_session
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_data.dict()
        result = models_database.DB.account_delete(db_file, user_session['active_website'], post_data_dict['account_id'])
        if result:
            return {
                "Response": "Successfully removed",
                "account_id": post_data_dict['account_id']
            }
# -------------------------
# END of ACCOUNTS section
# -------------------------


# -------------------------
# START of BACKUP section
# -------------------------
@app.post("/website/backup/create", status_code=200)
async def backup_create(post_model: models_post.BackupCreate):
    # The POST request should include a dictionary with the following:
    # website_id - The ID of the website that's to be backed up
    # account_id - The ID of the account that's going to be used for the backup
    global user_session
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_model.dict()
        domain = user_session['active_website']
        pass
# -------------------------
# END of BACKUP section
# -------------------------


# -------------------------
# START of WORDPRESS section
# -------------------------
@app.post("/wp/link", status_code=200)
async def wordpress_link(post_model: models_post.WordPressLink):
    global user_session
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_model.dict()
        domain = user_session['active_website']
        pass


@app.post("/wp/php/init", status_code=200)
async def wordpress_php_init(post_model: models_post.WordPressInit):
    global user_session
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_model.dict()
        website_id = user_session['active_website']
        account_id = post_data_dict['account_id']
        account_dict = models_database.DB.account_get(db_file, website_id, account_id)
        if account_dict['type'] == "FTP":
            ftp_upload_result = models_connection.FTP.upload_wpmt_php_client_ftp(account_dict['hostname'], account_dict['username'], account_dict['password'], account_dict['port'], account_dict['path'])
            return ftp_upload_result
        else:
            return{
                "Response": "Failure",
                "Message": "router.wordpress_init: Selected protocol not yet implemented"
            }


@app.get("/wp/php/core/version", status_code=200)
async def wordpress_php_core_version():
    global user_session
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        command = {
            "type": "wp-core",
            "option": "version",
        }
        core_version = models_connection.WP.send_wp_request_php(db_file, user_session['active_website'], command)
        return {
            "Response": "Success",
            "Result": core_version
        }


@app.get("/wp/php/plugin/list", status_code=200)
async def wordpress_php_core_version():
    global user_session
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        command = {
            "type": "wp-plugin",
            "option": "list",
        }
        # Here we send the request that runs the PHP code on the host server
        # The response is a mangled list of all plugins on the webiste
        plugin_str = models_connection.WP.send_wp_request_php(db_file, user_session['active_website'], command)
        # Therefore before returning it we first need to edit the string
        result = models_connection.WP.wp_plugin_list_cleanup(plugin_str)
        return {
            "Response": "Success",
            "Result": result
        }


# -------------------------
# END of WORDPRESS section
# -------------------------




if __name__ == '__main__':
    # TODO: Add error handling for when the default port is not available
    uvicorn.run(app, host='localhost', port=13332)