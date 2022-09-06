from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import log, db, user, website, account, backup, php, ssh
from models import config
import uvicorn
import logging
import argparse


# Initializing the server
app = FastAPI()
# Importing multiple routers into the server
# Source: https://fastapi.tiangolo.com/tutorial/bigger-applications/#import-fastapi
for item in [log, db, user, website, account, backup, php, ssh]:
    app.include_router(item.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def define_params():
    # Reading CLI input
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='WordPress Multi Tool Client backend'
    )
    parser.add_argument('-p', '--port', default=13332, help='The port on which the backend will start')
    parser.add_argument('-d', '--debug', action=argparse.BooleanOptionalAction, help='Enables debug logging level')
    return parser.parse_args()


def check_log_level():
    cli_parameters = define_params()
    if cli_parameters.debug is True:
        config.log_level = "DEBUG"
        return "DEBUG"
    else:
        config.log_level = "ERROR"
        return "ERROR"


if __name__ == '__main__':
    # Retrieving the CLI parameters
    cli_parameters = define_params()
    # Setting the debug level
    logging.basicConfig(filename=config.filename, level=check_log_level())
    try:
        uvicorn.run(app, host='localhost', port=int(cli_parameters.port))
    except TypeError as err:
        logging.error("Invalid port type. Integer is required")
        exit(err)