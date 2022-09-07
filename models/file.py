from os.path import expanduser, isfile, join
from pathlib import Path
from models import config


class File:
    @staticmethod
    def config_setup():
        home = expanduser('~')
        if not isfile(config.config_file):
            try:
                Path(join(home, 'WPMT', 'config')).mkdir(parents=True, exist_ok=True)
                config_file = open(config.config_file, 'w')
                config_file.write('')
                config_file.close()
                return True
            except IOError as err:
                # TODO: Add a Logger function which saves the issue
                print("ERROR: Couldn't create config.json, Stacktrace: ", err)
                return False
            except:
                return False
        else:
            return True

    @staticmethod
    def db_setup():
        home = expanduser('~')
        if not isfile(config.db_file):
            try:
                Path(join(home, 'WPMT', 'db')).mkdir(parents=True, exist_ok=True)
                db_file = open(config.db_file, 'w')
                db_file.write('')
                db_file.close()
                return True
            except IOError as err:
                # TODO: Add a Logger function which saves the issue
                print("ERROR: Couldn't create wpmt.db, Stacktrace: ", err)
                return False
            except:
                return False
        else:
            return True

    @staticmethod
    def log_setup():
        home = expanduser('~')
        if not isfile(config.log_file):
            try:
                Path(join(home, 'WPMT', 'log')).mkdir(parents=True, exist_ok=True)
                config_file = open(config.log_file, 'w')
                config_file.write('')
                config_file.close()
                return True
            except IOError as err:
                # TODO: Add a Logger function which saves the issue
                print("ERROR: Couldn't create log.txt, Stacktrace: ", err)
                return False
            except:
                return False
        else:
            return True