import datetime
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


def ip_init():
    database = db_connect()
    cursor = database.cursor()
    cursor.execute("DROP TABLE IF EXISTS pf_ip_ban;")
    cursor.execute(
        "CREATE TABLE pf_ip_ban (id SERIAL PRIMARY KEY, ip CIDR UNIQUE, updated_at timestamp without time zone, source character varying);"
    )
    cursor.execute(
        "INSERT INTO pf_ip_ban (ip, updated_at, source) VALUES ('209.229.0.0/16', '2019-04-07 11:11:25-07', 'emerging');"
    )
    cursor.execute(
        "INSERT INTO pf_ip_ban (ip, updated_at, source) VALUES ('219.229.0.2', '2019-04-14 11:11:25-07', 'emerging');"
    )
    cursor.close()
    database.commit()
    database.close()


def ip_get():
    database = db_connect()
    cursor = database.cursor()
    cursor.execute("select ip from pf_ip_ban;")
    results = cursor.fetchall()
    cursor.close()
    database.commit()
    database.close()
    return results


def ip_add(data):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    database = db_connect()
    cursor = database.cursor()

    any_204 = 0
    for entry in data:
        try:
            IP = entry["IP"]
            source = entry["source"]
        except KeyError as e:
            return (str(e) + " key is missing", 400)
        if "/" not in IP:
            IP = IP + "/32"
        values = (IP, time, source)
        try:
            cursor.execute(
                "INSERT INTO pf_ip_ban (ip, updated_at, source) VALUES (%s, %s, %s);",
                values,
            )
        # Most likely a problem with the CIDR
        except psycopg2.DataError as e:
            database.rollback()
            return (str(e), 400)
        # Unicity clause
        except psycopg2.IntegrityError as e:
            message = str(e)
            status_code = 200
            database.rollback()
        else:
            any_204 = 1
    database.commit()
    cursor.close()
    database.close()
    if any_204:
        return ("", 204)
    elif status_code == 200:
        return (message, status_code)
    else:
        return ("How did you get there?", 400)


def ip_delete(IP):
    if "/" not in IP:
        IP = IP + "/32"
    values = (IP,)
    database = db_connect()
    cursor = database.cursor()
    cursor.execute("DELETE FROM pf_ip_ban WHERE IP=%s;", values)
    cursor.close()
    database.commit()
    database.close()
    return ("", 204)
