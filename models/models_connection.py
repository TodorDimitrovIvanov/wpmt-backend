import json
from typing import Optional
from ftplib import FTP as FTPcontroller
from ftplib import all_errors
import requests
import router
from os.path import expanduser, isfile, join
from pathlib import Path

user_home = expanduser('~')

__app_headers__ = {
    'Host': 'cluster-eu01.wpmt.org',
    'User-Agent': 'WPMT-Client-API/1.0',
    'Referer': 'http://localhost:13337/models_connection.py',
    'Content-Type': 'application/json'
}


class Connection:

    @staticmethod
    def connection_start(conn_type: str, hostname: str, username: str, password: str, port: int, path: str):

        pass

    @staticmethod
    def download_php_client():
        if not isfile(join(user_home, 'WPMT', 'config', 'wp-multitool.php')):
            try:
                Path(join(user_home, 'WPMT', 'config')).mkdir(parents=True, exist_ok=True)
                client_file = open(join(user_home, 'WPMT', 'config', 'wp-multitool.php'), 'wb')
                client_file_contents = requests.get(router.__wpmt_php_client_url__)
                client_file.write(client_file_contents.content)
                client_file.close()
                return True
            except IOError as err:
                message = "[Client][Connection][Error][01]: Can't download the wpmt-client file. Full error: " + str(err)
                router.send_to_logger("error", message, client_id=None, client_email=None)
                return False
            except:
                return False
        else:
            return True


class FTP:
    @staticmethod
    def start(hostname: str, username: str, password: str, port: int, path: str):
        try:
            ftp_conn = FTPcontroller()
            ftp_conn.connect(hostname, port)
            ftp_conn.login(username, password)
            return ftp_conn
        except all_errors as err:
            message = "[Client][FTP][Error][01]: Can't connect to host. Full error: " + str(err)
            router.send_to_logger("error", message, client_id=None, client_email=None)
            return None

    @staticmethod
    def upload_wpmt_php_client():
        if isfile(join(user_home, 'WPMT', 'config', 'wp-multitool.php')):
            try:
                Path(join(user_home, 'WPMT', 'config')).mkdir(parents=True, exist_ok=True)
                client_file = open(join(user_home, 'WPMT', 'config', 'wp-multitool.php'), 'wb')
                ftp_conn = FTP.start()
                result = ftp_conn.storbinary('STOR wp-multitool.php', client_file)
                ftp_conn.close
                if result == "226 Transfer complete":
                    return True
                else:
                    return False
            # TODO: Add proper error handling here
            except:
                return False

    @staticmethod
    def get_cwd(hostname: str, username: str, password: str, port: int):
        ftp_conn = FTP.start(hostname, username, password, port)
        result = ftp_conn.pwd()
        ftp_conn.close()
        return result

    # TODO: Not core functionality but would be nice to have it
    @staticmethod
    def search_wp_config():
        ftp_conn = FTP.start()
        root_path = ftp_conn.pwd()
        root_search = ftp_conn.retrlines('LIST *wp-config*')
        print("FTP.search_wp_config: First Search", root_search, "\nType: ", type(root_search))




class SSH:
    pass


class SFTP:
    pass


class IMAP:
    pass


