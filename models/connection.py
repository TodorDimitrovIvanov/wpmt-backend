import base64
import errno
import io
import json
import os
import time
from typing import Optional
from ftplib import FTP as FTPcontroller
from ftplib import all_errors
import ftplib

import paramiko
import requests
from routers import log
from os.path import expanduser, isfile, join
from pathlib import Path
from models import database

user_home = expanduser('~')
__ftp_sleep_interval__ = 0.1

__app_headers__ = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'Accept-Language': 'en-US,en;q=0.9'
}


class WP:

    @staticmethod
    def wp_php_request_send(db_file, active_website: str, command: dict, data: dict=None):
        if data is None:
            website_dict = database.DB.db_site_get_id(db_file, active_website)
            website_domain = website_dict['domain']
            url = "http://" + str(website_domain) + "/wp-multitool.php?type=" + command['type'] + "&option=" + command['option']
            send_request = requests.get(url, headers=__app_headers__)
            print("[DEBUG]WP.wp_php_request_send: URL: ", url)
            #print("[DEBUG]WP.wp_php_request_send: ", send_request.content.decode())
            return send_request.content.decode()
        else:
            website_dict = database.DB.db_site_get_id(db_file, active_website)
            website_domain = website_dict['domain']
            # TODO: Add a check if the post_data_dict parameter we receive in this function has a "version" field
            # And if yes then create a new URL that includes it, provided the PHP Payload has this feature implemented
            url = "http://" + str(website_domain) + "/wp-multitool.php?type=" + command['type'] + "&option=" + command[
                'option'] + "&data=" + data['name']
            send_request = requests.get(url, headers=__app_headers__)
            print("[DEBUG]WP.wp_php_request_send: URL: ", url)
            # print("[DEBUG]WP.wp_php_request_send: ", send_request.content.decode())
            return send_request.content.decode()

    @staticmethod
    def wp_php_list_cleanup(plugin_str: str):
        for character in ['[',']', '\\']:
            plugin_str = plugin_str.replace(character, "")
        # Remove the extra { and } chars
        plugin_str = plugin_str[1:]
        plugin_str = plugin_str[:-1]
        # Here we split the string into a list
        plugin_list = plugin_str.split('},{')
        plugin_dict_list = {}
        # And finally, we fill a dictionary of the plugin dictionaries
        for index, element in enumerate(plugin_list):
            if index == 0:
                element = ''.join((element,'}'))
                # We don't need the headers in the dict, do we?
                plugin_dict_list[index+1] = json.loads(element)
            elif index == len(plugin_list)-1:
                element = ''.join(('{', element))
                plugin_dict_list[index+1] = json.loads(element)
            else:
                element = ''.join(('{', element, '}'))
                plugin_dict_list[index+1] = json.loads(element)
        return plugin_dict_list

    @staticmethod
    def wp_ssh_request_findroot(ssh_conn: paramiko.SSHClient):
        stdin1, stdout1, stderr1 = ssh_conn.exec_command("find . -name \"wp-config.php\"")
        print("[DEBUG]: models_connection.WP.wp_ssh_request_send: ", "\nSTDOUT: ", str(stdout1), "\nSTDERR: ", str(stderr1))


    @staticmethod
    def wp_ssh_request_send(db_file, active_website: str, account_id: str, command: str, data: dict=None):
        website_dict = database.DB.db_site_get_id(db_file, active_website)
        website_domain = website_dict['domain']
        account_dict = database.DB.account_get(db_file, active_website, account_id)
        if account_dict['type'] != "SSH":
            return {
                "Response": "Error",
                "Message": "The requested functionality is supported only on SSH connections"
            }
        else:
            ssh_conn = paramiko.SSHClient()
            ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            if account_dict['path'] != "/":
                #print("Base64 Key: ", account_dict['path'])
                #print("String Key: ", base64.b64decode(account_dict['path']))
                #keyFile = io.StringIO(account_dict['path'])
                privkey = paramiko.RSAKey.from_private_key(io.StringIO(base64.b64decode(account_dict['path']).decode()))
                #print("[DEBUG]: models_connection.WP.wp_ssh_request_send: Type: ", type(privkey))
                ssh_conn.connect(account_dict['hostname'], username=account_dict['username'], password=account_dict['password'], port=account_dict['port'], pkey=privkey)
                stdin, stdout, stderr = ssh_conn.exec_command(command)
                #print("[DEBUG]: models_connection.WP.wp_ssh_request_send: ", "\n\tSTDOUT: ", stdout.readlines(), "\n\tSTDERR: ", stderr.readlines())
                result = stdout.readlines()
                ssh_conn.close()
                return {
                    "Response": "Success",
                    "Message": result
                }
            else:
                # Else we need to implement a SSH conenction without a Private Key
                ssh_conn.connect(host=account_dict['hostname'], username=account_dict['username'], password=account_dict['password'], port=account_dict['port'])
                stdin, stdout, stderr = ssh_conn.exec_command(command)
                result = stdout.readlines()
                ssh_conn.close()
                return {
                    "Response": "Success",
                    "Message": result
                }


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
            log.send_to_logger("error", message, client_id=None, client_email=None)
            return None

    @staticmethod
    def upload_wpmt_php_client_ftp(hostname: str, username: str, password: str, port: int, path: str):
        if isfile(join(user_home, 'WPMT', 'config', 'wp-multitool.php')):
            try:
                filesize = os.path.getsize(join(user_home, 'WPMT', 'config', 'wp-multitool.php'))
                if filesize > 0:
                    Path(join(user_home, 'WPMT', 'config')).mkdir(parents=True, exist_ok=True)
                    ftp_conn = FTP.start(hostname, username, password, port, path)
                    ftp_conn.set_pasv(True)
                    ftp_conn.encoding = "utf-8"
                    # TODO: We need a way to check whether the last char is '/'
                    if path != "":
                        ftp_command = "STOR " + path + "/wp-multitool.php"
                    else:
                        ftp_command = "STOR wp-multitool.php"
                    with open(join(user_home, 'WPMT', 'config', 'wp-multitool.php'), 'rb') as file:
                        result = ftp_conn.storlines(ftp_command, file)
                    ftp_conn.quit()
                    if str(result[0:3]) == "226":
                        # If the first three chars are 226 -> Transfer completed
                        return {
                            "Response": "Success",
                            "Message": "FTP.upload_wpmt_php_client: The wp-multitool.php file was uploaded successfully"
                        }
                    else:
                        return {
                            "Response": "Failure",
                            "Message": "FTP.upload_wpmt_php_client: The wp-multitool.php file was not uploaded properly",
                            "Error": result
                        }
                else:
                    return {
                        "Response": "Failure",
                        "Message": "FTP.upload_wpmt_php_client: The wp-multitool.php file is empty",
                    }
            # TODO: Add proper error handling here
            except ftplib.all_errors as err:
                return {
                    "Response": "Failure",
                    "Message": "FTP.upload_wpmt_php_client: The wp-multitool.php file is missing",
                    "Error": str(err)
                }
            except ftplib.error_perm as err:
                return {
                    "Response": "Failure",
                    "Message": "FTP.upload_wpmt_php_client: Unable to upload the wp-multitool.php file. Permissions error",
                    "Error": str(err)
                }
        else:
            return {
                "Response": "Failure",
                "Message": "FTP.upload_wpmt_php_client: The wp-multitool.php file is missing"
            }

    @staticmethod
    def ftp_download_to_local(ftp_conn, destination_dir, path="/"):
        # This function will automatically recreate the dir structure from the remote host on the local machine
        # Since it runs recursively, it will also download all of the files and place the
        # Source: http://rizwanansari.net/download-all-files-from-ftp-in-python/
        global __ftp_sleep_interval__
        for elem in [ftp_conn, destination_dir]:
            if elem is None or elem == "":
                return{
                    "Response": "Failure",
                    "Message": "FTP.ftp_download_to_local: Missing parameters"
                }
        try:
            ftp_conn.cwd(path)
            os.chdir(destination_dir)
            FTP.ftp_create_local_dir(destination_dir[0:len(destination_dir)-1] + path)
            print("Created: " + destination_dir[0:len(destination_dir)-1] + path)
        except OSError:
            pass
        except ftplib.error_perm:
            return {
                "Response": "Failure",
                "Messsage": "FTP.ftp_download_to_local: Can't access folder [" + path + "]."
            }

        try:
            ftp_filelist = ftp_conn.nlst()
            # TODO: Here we need to retrieve the total number of files and folders to be downloaded
            # And pass it to the /backup/monitor/file/total endpoint (to be added)
        except ftplib.error_perm as err:
            if str(err) == "550 No files found":
                print("No files found in folder. Error: ", str(err))

        for file in ftp_filelist:
            # TODO: Here we need to add a counter that increments with each file
            # And pass it to the /backup/monitor/file/current endpoint (to be added)
            time.sleep(__ftp_sleep_interval__)
            try:
                ftp_conn.cwd(path + file + "/")
                FTP.ftp_download_to_local(ftp_conn, destination_dir, path + file + "/")
            except ftplib.error_perm:
                # If not a folder then we download the file
                os.chdir(destination_dir[0:len(destination_dir) - 1] + path)
                try:
                    ftp_conn.retrbinary("RETR " + file, open(os.path.join(destination_dir + path, file),"wb").write)
                    print("Downloaded in Binary: " + file)
                except:
                    return {
                        "Response": "Failure",
                        "Messsage": "FTP.ftp_download_to_local: Can't download file [" + file + "]."
                    }
        return

    @staticmethod
    def ftp_create_local_dir(path):
        try:
            os.makedirs(path)
        except OSError as err:
            if err.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    @staticmethod
    def download_php_client():
        # This function downloads a copy of the wp-multitool.php file to the user's machine
        if not isfile(join(user_home, 'WPMT', 'config', 'wp-multitool.php')):
            try:
                Path(join(user_home, 'WPMT', 'config')).mkdir(parents=True, exist_ok=True)
                client_file = open(join(user_home, 'WPMT', 'config', 'wp-multitool.php'), 'wb')
                client_file_contents = requests.get(log.__wpmt_php_client_url__)
                client_file.write(client_file_contents.content)
                client_file.close()
                return True
            except IOError as err:
                message = "[Client][Connection][Error][01]: Can't download the wpmt-client file. Full error: " + str(err)
                log.send_to_logger("error", message, client_id=None, client_email=None)
                return False
            except:
                return False
        else:
            return True

    @staticmethod
    def get_cwd(hostname: str, username: str, password: str, port: int):
        ftp_conn = FTP.start(hostname, username, password, port)
        result = ftp_conn.pwd()
        ftp_conn.close()
        return result

    @staticmethod
    def search_wp_config():
        # TODO: We should build a function that finds all files named 'wp-config.php'
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


