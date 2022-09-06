from fastapi import APIRouter
from models import post, database, config, file

router = APIRouter()
db_file = config.db_file
db_source = config.db_source
db_tables = config.db_tables


# Functions below are to be removed once development is completed
# They provide utility for debugging the App and are most likely a major security risk
@router.get("/db/check")
def read_root():
    if file.db_setup() and file.config_setup():
        return {"Response: Success"}
    else:
        return {"Response: Failure"}


@router.get("/db/structure", status_code=200)
def db_struct_get():
    result = database.DB.db_struct_list(db_file)
    return result


@router.get("/db/init", status_code=200)
def db_init():
    database.DB.init(db_source, db_file)
    return {
        "Response": "DB Initialized"
    }


@router.get("/db/export", status_code=200)
def db_export():
    dictComplete = {}
    for index, item in enumerate(db_tables):
        print(db_tables)
        result = database.DB.db_table_list(db_file, item)
        dictComplete[item] = result
    return dictComplete


@router.get("/db/import", status_code=200)
def db_import():
    pass


@router.post("/db/list", status_code=200)
def db_list(post_data: post.DBSearch):
    post_data_dict = post_data.dict()
    result = database.DB.db_table_list(db_file, post_data_dict['table_name'])
    return result
