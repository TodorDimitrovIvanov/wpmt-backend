from fastapi import FastAPI
from typing import Optional
from file import File
from db import DB

# This is an ASGI (Asynchronous Server Gateway Interface) server on which the API runs
# Source: https://www.uvicorn.org/
import uvicorn

app = FastAPI()

# -------------------------
# Temporary code
# When live the API should be able to retrieve the DB settings (and others) from the config.json file
db_source = "/home/todor/DbSchema/Schemas/wpmt-prototype-exported.sql"
db_file = "/home/todor/WPMT/db/wpmt.db"

# -------------------------
# DUMMY DATA
# We use these variables for testing the DB calls
client_id = "UEU00002"
client_key = "UEU00002-K1"
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

@app.get("/db/structure", status_code=200)
def db_struct_get():
    result = DB.db_struct_list(db_file)
    return result
# SYSTEM section
# -------------------------



# -------------------------
# USER Section
@app.post("/user/add")
async def user_add():
    DB.db_user_add(db_file,client_id,client_key,email,name,service,notifications,icon)


@app.get("/user/get", status_code=200)
def user_get():
    result = DB.db_user_get(db_file, client_id)
    return result


@app.get("/user/all", status_code=200)
def user_all():
    result = DB.db_user_all(db_file)
    return result
# USER section
# -------------------------


# -------------------------
# SITE section
@app.post("/site/add", status_code=200)
def db_site_add():
    DB.db_site_add(db_file, website_id, client_id, domain, domain_exp, certificate, cert_exp)


@app.get("/site/get", status_code=200)
def db_site_get():
    result = DB.db_site_get(db_file, website_id)
    return result


@app.get("/site/all", status_code=200)
def db_site_all():
    result = DB.db_site_all(db_file, client_id)
    return result
# SITE section
# -------------------------


if __name__ == '__main__':
    # TODO: Add error handling for when the default port is not available
    uvicorn.run(app, host='localhost', port=13332)