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


# INSERT INTO USERS (api_user, password, active) VALUES ('machine.example.com', 'uuid', 1);
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    database = db_connect()
    cursor = database.cursor()
    cursor.execute("SELECT password, active FROM users WHERE api_user=%s;", (username,))
    results = cursor.fetchone()
    cursor.close()
    database.close()
    if results[0] != password or results[1] != 1:
        return False
    return True


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
        "INSERT INTO pf_ip_ban (ip, updated_at, source) VALUES ('198.51.100.0/26', '2019-04-07 11:11:25-07', 'init');"
    )
    cursor.execute(
        "INSERT INTO pf_ip_ban (ip, updated_at, source) VALUES ('198.51.100.212', '2019-04-14 11:11:25-07', 'init');"
    )
    cursor.close()
    database.commit()
    database.close()


def ip_get(order=None):
    database = db_connect()
    cursor = database.cursor()
    if order == "ip":
        cursor.execute("SELECT ip FROM pf_ip_ban ORDER BY ip;")
    else:
        cursor.execute("SELECT ip FROM pf_ip_ban;")
    results = cursor.fetchall()
    cursor.close()
    database.commit()
    database.close()
    return results


def ip_add(data):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    database = db_connect()
    cursor = database.cursor()

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
                "INSERT INTO pf_ip_ban (ip, updated_at, source) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
                values,
            )
        # Most likely a problem with the CIDR
        except psycopg2.DataError as e:
            database.rollback()
            return (str(e), 400)
        else:
            database.commit()
    database.commit()
    cursor.close()
    database.close()
    return ("", 204)


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


def ip_count():
    database = db_connect()
    cursor = database.cursor()
    cursor.execute("SELECT COUNT(ip) from pf_ip_ban;")
    results = cursor.fetchone()[0]
    cursor.close()
    database.commit()
    database.close()
    return results
