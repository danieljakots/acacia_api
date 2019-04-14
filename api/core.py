#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response

from .tools import require_appkey, require_auth, ip_get, ip_add
# from tools import require_appkey, require_auth, ip_get, ip_add


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


@app.route("/post-test", methods=("POST",))
@require_auth
def post_test():
    if request.form:
        resp = jsonify(request.form.to_dict())
        return resp
    if request.json:
        resp = jsonify(request.get_json())
        return resp
    return "nope"


@app.route("/ua")
def ua():
    headers = dict(request.headers.items())
    return jsonify({"User-Agent": headers["User-Agent"]})


@app.route("/headers")
@require_appkey
def headers():
    headers = dict(request.headers.items())
    return jsonify(headers)


@app.route("/v1/pf", methods=("GET",))
@require_appkey
def pf_get():
    results = ip_get()
    return jsonify(results)


@app.route("/v1/pf", methods=("POST",))
@require_appkey
def pf_post():
    if request.form:
        post_data = request.form.to_dict()
        if "IP" not in post_data.keys() or "source" not in post_data.keys():
            return make_response(jsonify({"error": "Bad Request"}), 400)
        (message, status_code) = ip_add(post_data["IP"], post_data["source"])
    if request.json:
        data = request.get_json()
        any_204 = 0
        for entry in data:
            try:
                IP = entry["IP"]
                source = entry["source"]
            except KeyError:
                return make_response(jsonify({"error": "Bad Request"}), 400)
            (message, status_code) = ip_add(IP, source)
            if status_code == 400:
                return (jsonify(message), status_code)
            elif status_code == 204:
                any_204 = 1
        # As long we had at least one 204, that's what we will return
        if any_204 == 1:
            status_code = 204
    return (jsonify(message), status_code)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
    # app.run(host='127.0.0.1', port=8080, debug=False)
