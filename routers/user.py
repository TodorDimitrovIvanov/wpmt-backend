from fastapi import HTTPException, Request, APIRouter
from models import post, database, config
from models.state import State as state
from models.session import Session as session
from routers import log
import requests
import logging
import json
from json import JSONDecodeError
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

router = APIRouter()
db_file = config.db_file
__cluster_url__ = config.cluster_url
__app_headers__ = config.app_headers

global user_session


@router.post("/user/add")
async def user_add(user: post.User):
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
        if database.DB.db_user_add(db_file, response_dict['client_id'], response_dict['client_key'],
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


@router.post("/user/get", status_code=200)
def user_get(search: post.UserSearch):
    result_dic = search.dict()
    result = database.DB.db_user_get(db_file, result_dic['client_key'], result_dic['email'])
    # If such user exists
    if len(result) >= 1:
        return result
    # If such user doesn't exist
    else:
        return {
            "Response": "Not Found"
        }


@router.get("/user/all", status_code=200)
def user_all():
    result = database.DB.db_user_all(db_file)
    # If there are any registered users
    if len(result) >= 1:
        return result
    # If there are no registered user
    else:
        return {
            "Response": "No users found"
        }


@router.post("/user/login")
async def login(login_model: post.UserLogin, request: Request):
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
            temp_sess = session.session_create(result_dic['email'], client_ip, platform.system())
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
        message = "[Client][API][Error][02]: Failed authentication attempt. Double-check email and public key or your internet connection."
        logging.debug(message)
        log.send_to_logger("error", message, client_id=None, client_email=result_dic['email'])
        return {
            "Response": "Error",
            "Message": "Failed authentication attempt. Double-check email and public key. "
        }
    except ValueError as err:
        message = "[Client][API][Error][01]: The provided key is malformed and can't be loaded. Full Error: " + str(err)
        print("Message: ", message)
        log.send_to_logger("error", message, client_id=None, client_email=result_dic['email'])
        return {
            "Response": "Error",
            "Message": "The provided key is corrupted or not in the correct format."
        }


@router.get("/user/state/sync")
async def sync():
    if session.session_get() is None:
        raise HTTPException(statuscode=403)
        return
    else:
        result = state.state_cluster_get()
        return result


@router.get("/user/state/get", status_code=200)
async def state_get():
    try:
        if session.session_get() is None:
            raise HTTPException(
                status_code=403,
                detail="Not Allowed")
        else:
            # TODO: We're up to here for the moment
            # We need to add a post model for checking the state on the Cluster
            # And it should have the client_id within it
            temp = state.state_local_get()
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


@router.get("/user/state/set", status_code=200)
async def state_set():
    if session.session_get() is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed")
    else:
        temp = state.state_local_generate()
        #print("DEBUG: Router.state_set.DICT: ", temp)
        result = state.state_local_set(temp)
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