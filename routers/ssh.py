from fastapi import FastAPI, HTTPException, Request, APIRouter
from models import post, connection


router = APIRouter()


@router.post("/wp/ssh/checkup")
async def wordpress_ssh_checkup():
    pass


@router.get("/wp/ssh/wpfind")
async def wordpress_ssh_core_version(post_model: post.AccountGet):
    global user_session
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_model.dict()
        if post_data_dict['account_id'] == "":
            return {
                "Response": "Error",
                "Message": "Missing SSH account"
            }
        else:
            command = "find $($HOME) -name \"wp-config.php\" | sed 's/\/wp\-config\.php//g' | sed 's/\.\///g'"
            core_version = connection.WP.wp_ssh_request_send(db_file, user_session['active_website'], account_id=post_data_dict['account_id'], command=command)
            return core_version


@router.get("/wp/ssh/core/version")
async def wordpress_ssh_core_version(post_model: post.AccountGet):
    global user_session
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_model.dict()
        if post_data_dict['account_id'] == "":
            return {
                "Response": "Error",
                "Message": "Missing SSH account"
            }
        else:
            command = "wppath=$(find -type d -name \"wp-multitool\"); cd $wppath; php wp-cli/wp-cli.phar core version"
            core_version = connection.WP.wp_ssh_request_send(db_file, user_session['active_website'], account_id=post_data_dict['account_id'], command=command)
            return core_version