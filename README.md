# Setup

Requirements:

```
Python version 3.9+
PIP version 3.9+
```

First we have to download the Git repo containing the Backend App:

```bash
git clone https://github.com/TodorDimitrovIvanov/wpmt-client-backend.git
```

OR

```json
git clone ssh://___USER___@172.104.246.196:1337/home/todorivanov/todorivanov.eu/public_html/WPMT/WPMT-User-API
```

Then we install the Python requirements with pip:

```bash
pip3.9 install --no-cache-dir -r requirements.txt
```

And finally we start the App like this:

```bash
python3.9 main.py -p INTEGER
```

***N.B: You must specify the port number as otherwise the script won't start***
