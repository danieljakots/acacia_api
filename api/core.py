#!/usr/bin/env python3

from flask import Flask, jsonify, request
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


# CREATE TABLE pf_ip_ban (id SERIAL PRIMARY KEY, ip INET, updated_at timestamp without time zone, source character varying);
# INSERT INTO pf_ip_ban (ip, updated_at, source) VALUES ('209.229.0.0/16', '2019-04-07 11:11:25-07', 'emerging');
@app.route("/v1/ban-pf", methods=("GET",))
@require_appkey
def ban_pf():
    database = db_connect()
    cursor = database.cursor()
    cursor.execute("select ip from pf_ip_ban;")
    results = cursor.fetchall()
    cursor.close()
    database.commit()
    database.close()
    print(results)
    return jsonify(results)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
    # app.run(host='127.0.0.1', port=8080, debug=False)
