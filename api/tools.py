from functools import wraps

from flask import request, abort


def nope():
    fake_msg = ("java.lang.NullPointerException: Attempt to invoke "
                "API method on a null object reference")
    abort(503, fake_msg)


# The actual decorator function
def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if request.headers.get('key') and request.headers.get('key') == "blih":
            return view_function(*args, **kwargs)
        else:
            nope()
    return decorated_function


# CREATE TABLE users (user TEXT, password TEXT, active INTEGER);
# INSERT INTO users
# VALUES (testbotirc3, 8d604831-623a-4e1b-b82a-618d82b18d5a, 1);
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    print(username, password)
    return username == 'qwe' and password == 'qwe'
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
