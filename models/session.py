from fastapi import HTTPException
from models import config, database
from routers.log import send_to_logger
import uuid

db_file = config.db_file
global user_session

class Session:

    @staticmethod
    def session_create(email, client_ip, client_os):
        if email is not None and email != "":
            try:
                db_query = database.DB.db_user_session(db_file, email)
                session_obj = {
                    "session_id": str(uuid.uuid1()),
                    "client_id": db_query['client_id'],
                    "client_ip": client_ip,
                    "client_os": client_os,
                    "email": email,
                    "service": db_query['service'],
                    "active_website": "",
                    "notifications": db_query['notifications'],
                    "promos": db_query['promos']
                }
                # Code below may be deprecated depending on how user sessions will be managed
                # Either with files or in memory. With the current setup it will managed in memory
                '''session_file = router.app_home + '/' + 'session'
                with open(session_file, 'a') as session_opened:
                    json.dump(session_obj, session_opened)'''
                global user_session
                user_session = session_obj
                return session_obj
            except OSError as e:
                message = "[Client][Session][Error][01]: Couldn't create session file. Full error message: " + str(e)
                send_to_logger("error", message, db_query[0])

    @staticmethod
    def session_get():
        try:
            global user_session
            if user_session is not None:
                return user_session
            else:
                return HTTPException(
                    status_code=403,
                    detail="Not Allowed"
                )
        except NameError as e:
            message = "[Client][API][Error][02]: This protected request lacks authentication."
            print(message)
