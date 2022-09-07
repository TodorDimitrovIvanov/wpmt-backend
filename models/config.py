from os.path import expanduser, isfile, join
from pathlib import Path

user_home = expanduser("~")

log_level = "ERROR"
log_file = Path(join(str(user_home), "WPMT", "log", "log.txt"))
db_file = Path(join(str(user_home), 'WPMT', 'db', 'wpmt.db'))
config_file = Path(join(str(user_home), 'WPMT', 'config', 'config.json'))

app_home = user_home + "/WPMT"
app_headers = {
    'Host': 'cluster-eu01.wpmt.org',
    'User-Agent': 'WPMT-Client-API/1.0',
    'Referer': 'http://localhost:13337/router.py',
    'Content-Type': 'application/json'
}

cors_allowed_origins = [
    "http://localhost:13332",
    "http://localhost:3000"
]

db_source = "./dbs/wpmt-v1.5.sql"
db_file = user_home + "/WPMT/db/wpmt.db"
db_tables = ["users", "website", "accounts", "wordpress", "backup", "transfer"]

cluster_name = "cluster-eu01.wpmt.org"
cluster_url = "http://cluster-eu01.wpmt.org"
cluster_logger_url = "http://cluster-eu01.wpmt.org/log/save"
cluster_locale = "EU"

