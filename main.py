from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import log, db, user, website, account, backup, php, ssh
from models import config, file
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
    parser.add_argument('-p', '--port', type=int, default=13332, help='The port on which the backend will start')
    parser.add_argument('-d', '--debug', action='store_true', help='Enables debug logging level')
    parser.set_defaults(port=True)
    return parser.parse_args()


def check_log_level(cli_parameters):
    if cli_parameters.debug is True:
        config.log_level = "DEBUG"
        return "DEBUG"
    else:
        config.log_level = "ERROR"
        return "ERROR"


if __name__ == '__main__':
    # Retrieving the CLI parameters
    parameters = define_params()
    print(parameters)
    # Verifying that the essential files are present
    if file.File.db_setup() and file.File.config_setup() and file.File.log_setup():
        # Setting the debug level
        logging.basicConfig(filename=config.log_file, level=check_log_level(parameters))
        try:
            if int(parameters.port) > 1:
                uvicorn.run(app, host='localhost', port=int(parameters.port))
            else:
                logging.error("Invalid port. Please enter port from 3000 to 15000")
        except TypeError as err:
            logging.error("Invalid port type. Integer is required")
            exit(err)
    else:
        logging.error("Error during essential file verification. Please verify that log/log.txt, db/wpmt.db and "
                      "config/config.json files exist")
