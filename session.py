import json
import uuid
import router
import models_database
from json import loads


class Session:

    @staticmethod
    def session_create(email, client_ip, client_os):
        if email is not None and email != "":
            try:
                db_query = models_database.DB.db_user_session(router.db_file, email)
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
                return session_obj
            except OSError as e:
                message = "[Client][Session][Error][01]: Couldn't create session file. Full error message: " + str(e)
                router.send_to_logger("error", message, db_query[0])

    @staticmethod
    def session_invalidate(session_obj):
        session_obj = None

    @staticmethod
    def session_get():
        session_file = router.app_home + '/' + 'session'
        try:
            with open(session_file, 'a') as session_opened:
                return session_opened.read()
        except OSError as e:
            message = "[Client][Session][Error][01]: Couldn't open session file. Full error message: " + str(e)
            router.send_to_logger("error", message)

    @staticmethod
    def session_get_elements(element):
        session_file = router.app_home + '/' + 'session'
        try:
            with open(session_file, 'a') as session_opened:
                temp_dict = loads(session_opened.read())
            return temp_dict[element]
        except OSError as e:
            message = "[Client][Session][Error][01]: Couldn't open session file. Full error message: " + str(e)
            router.send_to_logger("error", message)


    @staticmethod
    def session_set_active_website(website_id):
        pass
