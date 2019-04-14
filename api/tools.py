from functools import wraps
import os

from flask import request, abort

import psycopg2


def nope():
    fake_msg = (
        "java.lang.NullPointerException: Attempt to invoke "
        "API method on a null object reference"
    )
    abort(503, fake_msg)


# The actual decorator function
def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if request.headers.get("key") and request.headers.get("key") == "blih":
            return view_function(*args, **kwargs)
        else:
            nope()

    return decorated_function


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    print(username, password)
    return username == "qwe" and password == "qwe"
#     conn = sqlite3.connect('/home/api/api.db')
#     c = conn.cursor()
#     c.execute("SELECT password, active FROM users WHERE user=?",
#               (username,))
#     data = c.fetchone()
#     if data is None:
#         return False
#     db_password, active = data
#     if active == 0:
#         return False
#     return db_password == password


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            nope()
        return f(*args, **kwargs)

    return decorated


def db_connect():
    host = os.getenv("PG_HOST", "127.0.0.1")
    database = os.getenv("PG_DB", "api")
    user = os.getenv("PG_USER", "api")
    password = os.getenv("PG_PASSWORD")
    port = os.getenv("PG_PORT", "5432")
    database = psycopg2.connect(
        host=host, database=database, user=user, password=password, port=port
    )
    return database
