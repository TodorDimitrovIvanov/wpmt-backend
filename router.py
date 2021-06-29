from fastapi import FastAPI, HTTPException
from file import File
from db import DB
import models

# This is an  ASGI (Asynchronous Server Gateway Interface) server on which the API runs
# Source: https://www.uvicorn.org/
import uvicorn

app = FastAPI()

# -------------------------
# Temporary code
# When live the API should be able to retrieve the DB settings (and others) from the config.json file
from os.path import expanduser
user_home = expanduser("~")

db_source = "./dbs/wpmt.sql"
db_file = user_home + "/WPMT/db/wpmt.db"
print("DB File: " + db_file)

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
async def login(login: models.UserLogin):
    # Source: https://jordanisaacs.github.io/fastapi-sessions/guide/getting_started/
    result_dic = login.dict()
    result = DB.db_user_login(db_file, result_dic['email'], result_dic['client_key'])
    # To be continued
    # Not sure how to manage Sessions in FastApi just yet

# Functions below are to be removed once development is completed
# They provide utility for debugging the App and are a major security risk
@app.get("/db/structure", status_code=200)
def db_struct_get():
    result = DB.db_struct_list(db_file)
    return result

@app.get("/db/init", status_code=200)
def db_init():
    DB.db_init(db_source, db_file)
    return "Request Received"

# SYSTEM section
# -------------------------



# -------------------------
# USER Section
@app.post("/user/add")
async def user_add(user: models.User):
    result_dic = user.dict()
    DB.db_user_add(db_file, result_dic['client_id'], result_dic['client_key'], result_dic['email'],
                   result_dic['name'], result_dic['service'], result_dic['notifications'], result_dic['icon'])


@app.post("/user/get", status_code=200)
def user_get(search: models.UserSearch):
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
def db_site_add(website: models.Website):
    result_dic = website.dict()
    DB.db_site_add(db_file, result_dic['website_id'], result_dic['client_id'], result_dic['domain'],
                   result_dic['domain_exp'], result_dic['certificate'], result_dic['certificate_exp'])


@app.post("/website/get", status_code=200)
def db_site_get(search: models.WebsiteSearch):
    result_dic = search.dict()
    result = DB.db_site_get(db_file, result_dic['client_id'], result_dic['domain'])
    return result


@app.get("/website/all", status_code=200)
def db_site_all():
    result = DB.db_site_all(db_file, client_id)
    return result


@app.post("/website/user", status_code=200)
async def db_site_user(client: models.WebsiteUserSearch):
    result_dic = client.dict()
    result = DB.db_site_user(db_file, result_dic['client_id'])
    return result
# WEBSITE section
# -------------------------


if __name__ == '__main__':
    # TODO: Add error handling for when the default port is not available
    uvicorn.run(app, host='localhost', port=13332)