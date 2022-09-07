import logging
from fastapi import APIRouter
from models import config
import requests
import json

global user_session
router = APIRouter()


def send_to_logger(err_type, message, client_id=None, client_email=None):
    """:type
    """
    body = {
        "client_id": client_id,
        "client_email": client_email,
        "type": err_type,
        "message": message
    }
    logging.debug(body)
    try:
        send_request = requests.post(config.cluster_logger_url, data=json.dumps(body), headers=config.app_headers)
    except requests.exceptions.HTTPError as err2:
        logging.error("The log connection to the Cluster failed. Stacktrace: ", err2)





