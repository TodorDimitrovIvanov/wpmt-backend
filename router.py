from fastapi import FastAPI, HTTPException, Request
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import requests
import json

# Custom modules
import models_file
import models_database
import session
# These are POST body models that the API endpoints expect to receive
import models_post

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
db_source = "./dbs/wpmt-v1.1.sql"
db_file = user_home + "/WPMT/db/wpmt.db"
app_home = user_home + "/WPMT"

# -------------------------
__cluster_name__ = "cluster-eu01.wpmt.tech"
__cluster_url__ = "http://cluster-eu01.wpmt.tech"
__cluster_logger_url__ = "http://cluster-eu01.wpmt.tech/log/save"
__cluster_locale__ = "EU"
# -------------------------

# -------------------------
__app_headers__ = {
    'Host': 'cluster-eu01.wpmt.org',
    'User-Agent': 'WPMT-Auth/1.0',
    'Referer': 'http://cluster-eu01.wpmt.org/auth/verify',
    'Content-Type': 'application/json'
}
# -------------------------

# -------------------------
# System section
@app.get("/")
def read_root():
    if models_file.db_setup() and models_file.config_setup():
        return {"Response: Success"}
    else:
        return {"Response: Failure"}


@app.post("/login")
async def login(login_model: models_post.UserLogin, request: Request):
    # Source: https://jordanisaacs.github.io/fastapi-sessions/guide/getting_started/
    result_dic = login_model.dict()

    # Source: https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/#encryption
    # Here we encrypt the client's email address using the public key the client provides
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
    # Here we retrieve the client's IP address using the FastApi 'Request' class
    # Source: https://fastapi.tiangolo.com/advanced/using-request-directly/#use-the-request-object-directly
    client_ip = request.client.host


    if response['Response'] == "Success":
        import platform
        temp_sess = session.Session.session_create(result_dic['email'], client_ip, platform.system(), )
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


@app.get("/logout")
async def logout():
    global user_session
    user_session = None


# Functions below are to be removed once development is completed
# They provide utility for debugging the App and are a major security risk
@app.get("/db/structure", status_code=200)
def db_struct_get():
    result = models_database.DB.db_struct_list(db_file)
    return result


@app.get("/db/init", status_code=200)
def db_init():
    models_database.DB.db_init(db_source, db_file)
    return {
        "Response": "DB Initialized"
    }


def send_to_logger(err_type, message, client_id: None, client_email: None):
    global __app_headers__
    body = {
        "client_id": client_id,
        "client_email": client_email,
        "type": err_type,
        "message": message
    }
    send_request = requests.post(__cluster_logger_url__, data=json.dumps(body), headers=__app_headers__)
# SYSTEM section
# -------------------------


# -------------------------
# USER Section
@app.post("/user/add")
async def user_add(user: models_post.User):
    result_dic = user.dict()

    send_request = requests.post(__cluster_url__ + "/user/add", data=json.dumps(result_dic), headers=__app_headers__)
    response = (send_request.content).decode()
    response_dict = json.loads(response)

    if models_database.DB.db_user_add(db_file, response_dict['client_id'], response_dict['client_key'],
                                   result_dic['email'], result_dic['name'], result_dic['service'],
                                   result_dic['notifications'], result_dic['promos']):
        return {
            "Response": "Success",
            "client_id": response_dict['client_id'],
            "client_key": response_dict['client_key']
        }


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
# USER section
# -------------------------


# -------------------------
# WEBSITE section
@app.post("/website/add", status_code=200)
# Here we check whether the user has logged in before we allow him to add a website
# This is done via the "session_data" parameter
def website_add(website: models_post.Website):
    try:
        global user_session
        if user_session is None:
            raise HTTPException(statuscode=403)
        else:
            result_dic = website.dict()
            models_database.DB.db_site_add(db_file, result_dic['website_id'], user_session['client_id'], result_dic['domain'],
                                        result_dic['domain_exp'], result_dic['certificate'], result_dic['certificate_exp'])
            return {
                "Response": "Success"
            }
    except NameError:
        return HTTPException(status_code=403)
    # TODO: Add MySQL conn error handling


@app.post("/website/get", status_code=200)
def website_get(search: models_post.WebsiteSearch):
    try:
        global user_session
        if user_session is None:
            raise HTTPException(statuscode=403)
        else:
            result_dic = search.dict()
            result = models_database.DB.db_site_get(db_file, user_session['client_id'], result_dic['domain'])
            return result
    except NameError:
        return HTTPException(status_code=403)


# Note: This function should be removed as it could pose a security risk
# It's currently used for debugging purposes
@app.get("/website/all", status_code=200)
def website_all(search: models_post.WebsiteUserSearch):
    post_data_dict = search.dict()
    result = models_database.DB.db_site_all(db_file, post_data_dict['client_id'])
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
    # TODO: Add exception handling for MySQL errors
# WEBSITE section
# -------------------------


if __name__ == '__main__':
    # TODO: Add error handling for when the default port is not available
    uvicorn.run(app, host='localhost', port=13332)