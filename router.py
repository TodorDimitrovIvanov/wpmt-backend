from fastapi import FastAPI
from typing import Optional
from file import File
from db import DB

# This is an ASGI (Asynchronous Server Gateway Interface) server on which the API runs
# Source: https://www.uvicorn.org/
import uvicorn

app = FastAPI()

# Temporary code
# When live the API should be able to retrieve the DB settings (and others) from the config.json file
db_source = "/home/todor/DbSchema/Schemas/wpmt-prototype-exported.sql"
db_file = "/home/todor/WPMT/db/wpmt.db"

# Here we define the web-root path
# It will then route the request to the setup function
@app.get("/")
def read_root():
    if File.db_setup() and File.config_setup():
        #DB.db_init(db_source, db_file)
        DB.db_struct_list(db_file)
        return {"Init: Success"}
    else:
        return {"Init: Failure"}


@app.post("/user/add")
def user_add():
    pass


@app.get("/user/get", status_code=200)
def user_get():
    pass


if __name__ == '__main__':
    # TODO: Add error handling for when the default port is not available
    uvicorn.run(app, host='localhost', port=13332)