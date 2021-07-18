from os.path import expanduser, isfile, join
from pathlib import Path


class File:
    @staticmethod
    def config_setup():
        home = expanduser('~')
        if not isfile(join(home, 'WPMT', 'config', 'config.json')):
            try:
                Path(join(home, 'WPMT', 'config')).mkdir(parents=True, exist_ok=True)
                config_file = open(join(home, 'WPMT', 'config', 'config.json'), 'w')
                config_file.write('')
                config_file.close()
            except IOError as err:
                # TODO: Add a Logger function which saves the issue
                print("ERROR: Couldn't create config.json")
                return False
            except:
                return False
            finally:
                return True
        else:
            return True

    @staticmethod
    def db_setup():
        home = expanduser('~')
        if not isfile(join(home, 'WPMT', 'db', 'wpmt.db')):
            try:
                Path(join(home, 'WPMT', 'db')).mkdir(parents=True, exist_ok=True)
                db_file = open(join(home, 'WPMT', 'db', 'wpmt.db'), 'w')
                db_file.write('')
                db_file.close()
            except IOError as err:
                # TODO: Add a Logger function which saves the issue
                print("ERROR: Couldn't create wpmt.db")
                return False
            except:
                return False
            finally:
                return True
        else:
            return True

