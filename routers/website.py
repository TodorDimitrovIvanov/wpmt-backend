from fastapi import HTTPException, APIRouter
from models import post, database, config
from models.session import Session as session

router = APIRouter()
db_file = config.db_file
global user_session

@router.post("/website/add", status_code=200)
# Here we check whether the user has logged in before we allow him to add a website
# This is done via the "session_data" parameter
def website_add(website: post.Website):
    try:
        current_session = session.session_get()
        if current_session is None:
            raise HTTPException(statuscode=403)
        else:
            result_dic = website.dict()
            # Here we generate the ID of the website
            new_site_num = int(database.DB.db_site_count_get(db_file, current_session['client_id']))
            website_id = current_session['client_id'] + ":SITE-" + str(new_site_num + 1).zfill(4)

            if database.DB.db_site_add(db_file, website_id, current_session['client_id'], result_dic['domain'],
                                       result_dic['domain_exp'], result_dic['certificate'], result_dic['certificate_exp']):
                current_session['active_website'] = website_id
                return {
                    "Response": "Success",
                    "domain": result_dic['domain'],
                    "website_id": website_id,
                    "client_id": current_session['client_id']
                }
            else:
                return {
                    "Response": "Error",
                    "Message": "[Cluster][DB][03]: Failed adding data to DB"
                }
    except NameError:
        return HTTPException(status_code=403)


@router.post("/website/get", status_code=200)
def website_get(search: post.WebsiteSearch):
    try:
        if session.session_get() is None:
            raise HTTPException(status_code=403)
        else:
            result_dic = search.dict()
            result = database.DB.db_site_get(db_file, user_session['client_id'], result_dic['domain'])
            return result
    except NameError:
        return HTTPException(status_code=403)


@router.post('/website/get/id', status_code=200)
def website_get_id(search: post.WebsiteID):
    try:
        if session.session_get() is None:
            raise HTTPException(status_code=403)
        else:
            result_dic = search.dict()
            result = database.DB.db_site_get_id(db_file, result_dic['website_id'])
            return result
    except NameError:
        return HTTPException(status_code=403)


# Note: This function should be removed as it could pose a security risk
# It's currently used for debugging purposes
@router.get("/website/all", status_code=200)
def website_all():
    result = database.DB.db_site_all(db_file)
    return result


@router.post("/website/user", status_code=200)
async def website_user():
    try:
        if session.session_get() is not None:
            print(user_session['client_id'])
            result = database.DB.db_site_user(db_file, user_session['client_id'])
            return result
        else:
            raise HTTPException(status_code=403)
    except NameError:
        return HTTPException(status_code=403)


@router.post("/website/active/set")
async def website_active_set(post_data: post.WebsiteID):
    post_data_dict = post_data.dict()
    if session.session_get() is not None:
        user_session = session.session_get()
        try:
            sql_result = database.DB.db_site_get(db_file, user_session['client_id'], post_data_dict['website_id'])
            user_session['active_website'] = sql_result['website_id']
            return {
                "Response": "Success",
            }
        except KeyError as err:
            return {
                "Response": "Failure",
                "Message": "Most likely the provided website doesn't exist in the local DB"
            }
    else:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )


@router.get("/website/active/get")
async def website_active_get():
    if session.session_get() is not None:
        if user_session['active_website'] != "":
            return user_session
        else:
            return {
                "Response": "Error",
                "Message": "There's no website currently active"
            }
    else:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )