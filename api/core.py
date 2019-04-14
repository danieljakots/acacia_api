#!/usr/bin/env python3

import datetime

from flask import Flask, jsonify, request, abort
import psycopg2

from .tools import require_appkey, require_auth, db_connect
# from tools import require_appkey, require_auth, db_connect


app = Flask(__name__)


@app.route("/")
def hello():
    return jsonify("Hello world!")


@app.route("/ip")
def ip():
    return jsonify(origin=request.headers.get("X-Forwarded-For", request.remote_addr))


@app.route("/post", methods=("POST",))
@require_auth
def post():
    resp = jsonify(request.form.to_dict())
    resp.headers["X-OTHER"] = "ui"
    resp.headers["X-OTTER"] = "Not Jean Canard"
    return resp


@app.route("/ua")
def ua():
    headers = dict(request.headers.items())
    return jsonify({"User-Agent": headers["User-Agent"]})


@app.route("/headers")
@require_appkey
def headers():
    headers = dict(request.headers.items())
    return jsonify(headers)


@app.route("/v1/ban-pf", methods=("GET",))
@require_appkey
def ban_pf_get():
    database = db_connect()
    cursor = database.cursor()
    cursor.execute("select ip from pf_ip_ban;")
    results = cursor.fetchall()
    cursor.close()
    database.commit()
    database.close()
    return jsonify(results)


@app.route("/v1/ban-pf", methods=("POST",))
@require_appkey
def ban_pf_post():
    post_data = request.form.to_dict()
    if "IP" not in post_data.keys() or "source" not in post_data.keys():
        abort(400)
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "/" not in post_data["IP"]:
        post_data["IP"] = post_data["IP"] + "/32"
    values = (post_data["IP"], time, post_data["source"])
    database = db_connect()
    cursor = database.cursor()
    try:
        cursor.execute(
            "INSERT INTO pf_ip_ban (ip, updated_at, source) VALUES (%s, %s, %s);",
            values,
        )
    except psycopg2.DataError as e:
        return(jsonify(str(e)), 400)
    except psycopg2.IntegrityError as e:
        return(jsonify(str(e)), 200)
    cursor.close()
    database.commit()
    database.close()
    return ("", 204)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
    # app.run(host='127.0.0.1', port=8080, debug=False)
