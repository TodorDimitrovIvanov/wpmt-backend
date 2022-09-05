from fastapi import HTTPException, APIRouter
from models import post, database, config
from models.session import Session as session

router = APIRouter()
db_file = config.db_file


@router.post("/website/account/add", status_code=200)
async def account_add(post_data: post.Account):
    if session.session_get() is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed")
    else:
        current_session = session.session_get()
        if current_session['active_website'] == "" or None:
            return{
                "Response": "Error",
                "Message": "The Session is missing an 'active_website'."
            }
        else:
            # Here we retrieve the the data provided from the POST request
            post_data_dict = post_data.dict()
            # Here we generate the ID of the account that's being added
            last_account_id = database.DB.account_count(db_file, current_session['active_website'])
            account_id = current_session['active_website'] + ":ACC-" + str(last_account_id + 1).zfill(4)

            result = database.DB.account_add(db_file, account_id,
                                             current_session['active_website'], post_data_dict['type'],
                                             post_data_dict['hostname'], post_data_dict['username'],
                                             post_data_dict['password'], post_data_dict['port'],
                                             post_data_dict['path'])
            if result:
                return {
                    "Response": "Success",
                    "account_id": account_id
                }
            else:
                return {
                    "Response": "Error",
                    "Message": "No records found!"
                }



@router.post("/website/account/type/get", status_code=200)
async def account_type_get(post_data: post.AccountTypeGet):
    # This function will return all accounts of certain type (SSH,FTP, etc.) for the specified website
    if session.session_get() is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_data.dict()
        current_session = session.session_get()
        result = database.DB.accounts_type_get(db_file, current_session['active_website'], post_data_dict['account_type'])
        if result:
            return result
        else:
            return {
                "Response": "Error",
                "Message": "No records found!"
            }


@router.post("/website/account/all", status_code=200)
async def account_all():
    current_session = session.session_get()
    if current_session is None or current_session['active_website'] == "":
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
        return
    else:
        result = database.DB.accounts_all(db_file, current_session['active_website'])
        if result:
            return result
        else:
            return {
                "Response": "Error",
                "Message": "No records found!"
            }


@router.post("/website/account/get", status_code=200)
async def account_get(post_data: post.AccountGet):
    current_session = session.session_get()
    if current_session is None or current_session['active_website'] == "":
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
        return
    else:
        post_data_dict = post_data.dict()
        result = database.DB.account_get(db_file, current_session['active_website'], post_data_dict['account_id'])
        if result:
            return {
                "Response": "Success",
                "account": result
            }
        else:
            return{
                "Response": "Failure",
                "Message": "Account not found"
            }


@router.post("/website/account/delete", status_code=200)
async def account_delete(post_data: post.AccountGet):
    # This function expects to receive the account_id after the user is logged in and selects an account to be deleted.
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_data.dict()
        result = database.DB.account_delete(db_file, user_session['active_website'], post_data_dict['account_id'])
        if result:
            return {
                "Response": "Successfully removed",
                "account_id": post_data_dict['account_id']
            }