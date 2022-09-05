from fastapi import HTTPException, APIRouter
from models import post
from models.session import Session as session

router = APIRouter()


@router.post("/website/backup/create", status_code=200)
async def backup_create(post_model: post.BackupCreate):
    # The POST request should include a dictionary with the following:
    # website_id - The ID of the website that's to be backed up
    # account_id - The ID of the account that's going to be used for the backup
    if session.session_get() is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_model.dict()
        temp_session = session.session_get()
        domain = temp_session['active_website']
        pass