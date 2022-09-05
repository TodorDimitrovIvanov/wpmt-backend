from fastapi import HTTPException, APIRouter
from models import post, database, connection, config
from models.session import Session as session

router = APIRouter()
db_file = config.db_file


@router.post("/wp/php/checkup")
async def wordpress_php_checkup():
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        command_plugins = {
            "type": "wp-plugin",
            "option": "list",
        }
        plugin_str = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command_plugins)
        result = connection.WP.wp_php_list_cleanup(plugin_str)
        print("Plugins: ", result)
        command_themes = {
            "type": "wp-theme",
            "option": "list",
        }
        theme_str = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command_themes)
        result_theme = connection.WP.wp_php_list_cleanup(theme_str)
        print("Themes: ", result_theme)
        command_version = {
            "type": "wp-core",
            "option": "version",
        }
        version_str = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command_version)
        #result_version = models_connection.WP.wp_php_list_cleanup(version_str)
        print("Version: ", version_str)

        command_size = {
            "type": "file",
            "option": "size",
        }
        size_str = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command_size)
        #result_size = models_connection.WP.wp_php_list_cleanup(size_str)
        print("Size(kB): ", size_str)

@router.post("/wp/php/init", status_code=200)
async def wordpress_php_init(post_model: post.WordPressInit):
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_model.dict()
        website_id = user_session['active_website']
        account_id = post_data_dict['account_id']
        account_dict = database.DB.account_get(db_file, website_id, account_id)
        if account_dict['type'] == "FTP":
            ftp_upload_result = connection.FTP.upload_wpmt_php_client_ftp(account_dict['hostname'], account_dict['username'], account_dict['password'], account_dict['port'], account_dict['path'])
            return ftp_upload_result
        else:
            return{
                "Response": "Failure",
                "Message": "router.wordpress_init: Selected protocol not yet implemented"
            }


@router.get("/wp/php/db/setup", status_code=200)
async def wordpress_dbtools_setup():
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        command = {
            "type": "db",
            "option": "setup",
        }
        db_result = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command)
        return {
            "Response": "Success",
            "Result": db_result
        }


@router.get("/wp/php/db/settings", status_code=200)
async def wordpress_dbsettings_get():
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        command = {
            "type": "db",
            "option": "settings",
        }
        db_result = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command)
        return {
            "Response": "Success",
            "Result": db_result
        }


@router.get("/wp/php/db/backup", status_code=200)
async def wordpress_db_backup():
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        command = {
            "type": "db",
            "option": "export",
        }
        db_result = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command)
        return {
            "Response": "Success",
            "Result": db_result
        }


@router.get("/wp/php/file/size", status_code=200)
async def wordpress_filesize_get():
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        command = {
            "type": "file",
            "option": "size",
        }
        file_result = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command)
        return {
            "Response": "Success",
            "Result": file_result
        }


@router.get("/wp/php/file/perm", status_code=200)
async def wordpress_fileperm_reset():
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        command = {
            "type": "file",
            "option": "permissions",
        }
        file_result = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command)
        return {
            "Response": "Success",
            "Result": file_result
        }


@router.get("/wp/php/file/backup", status_code=200)
async def wordpress_file_backup():
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        command = {
            "type": "file",
            "option": "backup",
        }
        file_result = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command)
        return {
            "Response": "Success",
            "Result": file_result
        }


@router.get("/wp/php/core/version", status_code=200)
async def wordpress_php_core_version():
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        command = {
            "type": "wp-core",
            "option": "version",
        }
        core_version = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command)
        return {
            "Response": "Success",
            "Result": core_version
        }


@router.get("/wp/php/core/reset")
async def wordpress_php_core_reset():
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        command = {
            "type": "wp-core",
            "option": "reset",
        }
        core_version = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command)
        return {
            "Response": "Success",
            "Result": core_version
        }


@router.get("/wp/php/plugin/list", status_code=200)
async def wordpress_php_plugin_list():
    if session.session_get() is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        command = {
            "type": "wp-plugin",
            "option": "list",
        }
        # Here we send the request that runs the PHP code on the host server
        # The response is a mangled list of all plugins on the webiste
        user_session = session.session_get()
        plugin_str = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command)
        # Therefore before returning it we first need to edit the string
        result = connection.WP.wp_php_list_cleanup(plugin_str)
        return {
            "Response": "Success",
            "Result": result
        }


@router.get("/wp/php/plugin/update", status_code=200)
async def wordpress_php_plugin_update(post_model: post.WordPressData):
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_model.dict()
        if post_data_dict['name'] == "":
            return {
                "Response": "Error",
                "Message": "Missing plugin name"
            }
        else:
            command = {
                "type": "wp-plugin",
                "option": "update",
            }
            update_result = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command, post_data_dict)
            return {
                "Response": "Success",
                "Result": update_result
            }


@router.get("/wp/php/plugin/enable", status_code=200)
async def wordpress_php_plugin_enable(post_model: post.WordPressData):
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_model.dict()
        if post_data_dict['name'] == "":
            return {
                "Response": "Error",
                "Message": "Missing plugin name"
            }
        else:
            command = {
                "type": "wp-plugin",
                "option": "enable",
            }
            change_result = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command, post_data_dict)
            return {
                "Response": "Success",
                "Result": change_result
            }


@router.get("/wp/php/plugin/disable", status_code=200)
async def wordpress_php_plugin_disables(post_model: post.WordPressData):
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_model.dict()
        if post_data_dict['name'] == "":
            return {
                "Response": "Error",
                "Message": "Missing plugin name"
            }
        else:
            command = {
                "type": "wp-plugin",
                "option": "disable",
            }
            change_result = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command, post_data_dict)
            return {
                "Response": "Success",
                "Result": change_result
            }


@router.get("/wp/php/theme/list", status_code=200)
async def wordpress_php_theme_list():
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        command = {
            "type": "wp-theme",
            "option": "list",
        }
        # Here we send the request that runs the PHP code on the host server
        # The response is a mangled list of all plugins on the webiste
        theme_str = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command)
        # Therefore before returning it we first need to edit the string
        result = connection.WP.wp_php_list_cleanup(theme_str)
        return {
            "Response": "Success",
            "Result": result
        }


@router.get("/wp/php/theme/update", status_code=200)
async def wordpress_php_plugin_update(post_model: post.WordPressData):
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_model.dict()
        if post_data_dict['name'] == "":
            return {
                "Response": "Error",
                "Message": "Missing theme name"
            }
        else:
            command = {
                "type": "wp-theme",
                "option": "update",
            }
            update_result = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command, post_data_dict)
            return {
                "Response": "Success",
                "Result": update_result
            }


@router.get("/wp/php/theme/enable", status_code=200)
async def wordpress_php_plugin_enable(post_model: post.WordPressData):
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_model.dict()
        if post_data_dict['name'] == "":
            return {
                "Response": "Error",
                "Message": "Missing plugin name"
            }
        else:
            command = {
                "type": "wp-theme",
                "option": "enable",
            }
            change_result = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command, post_data_dict)
            return {
                "Response": "Success",
                "Result": change_result
            }


@router.get("/wp/php/theme/disable", status_code=200)
async def wordpress_php_plugin_disable(post_model: post.WordPressData):
    user_session = session.session_get()
    if user_session is None:
        raise HTTPException(
            status_code=403,
            detail="Not Allowed"
        )
    else:
        post_data_dict = post_model.dict()
        if post_data_dict['name'] == "":
            return {
                "Response": "Error",
                "Message": "Missing plugin name"
            }
        else:
            command = {
                "type": "wp-theme",
                "option": "disable",
            }
            change_result = connection.WP.wp_php_request_send(db_file, user_session['active_website'], command, post_data_dict)
            return {
                "Response": "Success",
                "Result": change_result
            }