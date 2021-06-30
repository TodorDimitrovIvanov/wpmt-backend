import uuid


class Session():

    @staticmethod
    def session_create(client_id, client_ip, client_os, service, active_website, notifications):
        if None not in {client_id, client_os, service}:
            session_obj = {
                    "session_id": uuid.uuid1(),
                    "client_id": client_id,
                    "client_ip": client_ip,
                    "client_os": client_os,
                    "service": service,
                    "active_website": active_website,
                    "notifications": notifications
            }
            return session_obj

    @staticmethod
    def session_invalidate(session_obj):
        session_obj = None
