import socket

from fastapi import FastAPI, HTTPException
from file import File
from db import DB
from session import Session
# These are POST body models that the API endpoints expect to receive
import post_models

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
db_source = "./dbs/wpmt.sql"
db_file = user_home + "/WPMT/db/wpmt.db"

# -------------------------
# DUMMY DATA
# We use these variables for testing the DB calls
client_id = "EU-U-0000001"
client_key = "UEU00001-K1"
email = "test@domain.com"
name = "Test Dummy"
service = "Free"
notifications = "Disabled"
icon = "None"

website_id = "UEU00002-W1"
domain = "domain.com"
domain_exp = "02-Jun-2021"
certificate = "None"
cert_exp = "None"
# DUMMY DATA
# -------------------------


# -------------------------
# System section
@app.get("/")
def read_root():
    if File.db_setup() and File.config_setup():
        return {"Init: Success"}
    else:
        return {"Init: Failure"}


@app.post("/login")
async def login(login_model: post_models.UserLogin):
    # Source: https://jordanisaacs.github.io/fastapi-sessions/guide/getting_started/
    result_dic = login_model.dict()
    result = DB.db_user_login(db_file, result_dic['email'], result_dic['client_key'])

    if result != "[]" or "{}" & result is not None:
        import platform

        result_list = result[0]
        temp_sess = Session.session_create(client_id=result_list[0], client_ip=None, client_os=platform.system(), service=result_list[4], active_website=None, notifications=None)
        # Here we set the global variable to the newly created object
        global user_session
        user_session = temp_sess
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
    result = DB.db_struct_list(db_file)
    return result


@app.get("/db/init", status_code=200)
def db_init():
    DB.db_init(db_source, db_file)
    return "DB Init Started"

# SYSTEM section
# -------------------------


# -------------------------
# USER Section
@app.post("/user/add")
async def user_add(user: post_models.User):
    result_dic = user.dict()
    DB.db_user_add(db_file, result_dic['client_id'], result_dic['client_key'], result_dic['email'],
                   result_dic['name'], result_dic['service'], result_dic['notifications'], result_dic['icon'])


@app.post("/user/get", status_code=200)
def user_get(search: post_models.UserSearch):
    result_dic = search.dict()
    result = DB.db_user_get(db_file, result_dic['client_key'], result_dic['email'])
    return result


@app.get("/user/all", status_code=200)
def user_all():
    result = DB.db_user_all(db_file)
    return result
# USER section
# -------------------------


# -------------------------
# WEBSITE section
@app.post("/website/add", status_code=200)
# Here we check whether the user has logged in before we allow him to add a website
# This is done via the "session_data" parameter
def website_add(website: post_models.Website):
    try:
        global user_session
        if user_session is None:
            raise HTTPException(statuscode=403)
        else:
            result_dic = website.dict()
            DB.db_site_add(db_file, result_dic['website_id'], user_session['client_id'], result_dic['domain'],
                           result_dic['domain_exp'], result_dic['certificate'], result_dic['certificate_exp'])
    except NameError:
        return HTTPException(status_code=403)
    # TODO: Add MySQL conn error handling


@app.post("/website/get", status_code=200)
def website_get(search: post_models.WebsiteSearch):
    try:
        global user_session
        if user_session is None:
            raise HTTPException(statuscode=403)
        else:
            result_dic = search.dict()
            result = DB.db_site_get(db_file, user_session['client_id'], result_dic['domain'])
            return result
    except NameError:
        return HTTPException(status_code=403)
    # TODO: Add MySQL conn error handling


# Note: This function should be removed as it could pose a security risk
# It's currently used for debugging purposes
@app.get("/website/all", status_code=200)
def website_all():
    result = DB.db_site_all(db_file, client_id)
    return result


@app.post("/website/user", status_code=200)
async def website_user():
    try:
        global user_session
        if user_session is not None:
            print(user_session['client_id'])
            result = DB.db_site_user(db_file, user_session['client_id'])
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