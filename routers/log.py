import logging

from fastapi import FastAPI, HTTPException, Request, APIRouter

import requests
import json
import sched, time, datetime


# Custom modules
from fastapi.middleware.cors import CORSMiddleware

from models import file, post, database, connection
# These are POST body models that the API endpoints expect to receive
# This is an  ASGI (Asynchronous Server Gateway Interface) server on which the API runs
# Source: https://www.uvicorn.org/
import uvicorn



# -------------------------
# Temporary code
# When live the API should be able to retrieve the DB settings (and others) from the config.json file

api_main_router = APIRouter()
global user_session

logging.basicConfig(level=logging.DEBUG)


# -------------------------
__wpmt_php_client_url__ = ""


__app_headers__2__ = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'Accept-Language': 'en-US,en;q=0.9'
}

# -------------------------
# Daemon-like module for executing tasks at regular intervals
# It will be used for syncing the state of the App DB
scheduler = sched.scheduler(time.time, time.sleep)




router = APIRouter()



@api_main_router.get("/")
def read_root():
    if file.db_setup() and file.config_setup():
        return {"Response: Success"}
    else:
        return {"Response: Failure"}


def send_to_logger(err_type, message, client_id=None, client_email=None):
    global __app_headers__
    global user_session
    # TODO: Remove the parameters once its verified that the user_session is properly received
    #print("Send to Logger Debug. Client_id: ", user_session['client_id'], user_session['email'])
    body = {
        "client_id": client_id,
        "client_email": client_email,
        "type": err_type,
        "message": message
    }
    send_request = requests.post(__cluster_logger_url__, data=json.dumps(body), headers=__app_headers__)
    logging.debug(message)
# -------------------------
# END of SYSTEM section
# -------------------------

@api_main_router.post("/wp/link", status_code=200)
async def wordpress_link(post_model: post.WordPressLink):
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
# END of WORDPRESS section
# -------------------------




