#!/usr/bin/env python3

from flask import Flask, jsonify, request

from api import tools
from api import v1
from api import v2

app = Flask(__name__)


def hello():
    return jsonify("Hello world!")


def ip():
    return jsonify(origin=request.headers.get("X-Forwarded-For", request.remote_addr))


@tools.require_auth
def post():
    if request.form:
        resp = jsonify(request.form.to_dict())
    elif request.json:
        resp = jsonify(request.get_json())
    else:
        return "nope"
    resp.headers["X-OTHER"] = "ui"
    resp.headers["X-OTTER"] = "Not Jean Canard"
    return resp


def ua():
    headers = dict(request.headers.items())
    return jsonify({"User-Agent": headers["User-Agent"]})


@tools.require_appkey
def headers():
    headers = dict(request.headers.items())
    return jsonify(headers)


app.add_url_rule("/", view_func=hello)
app.add_url_rule("/ip", view_func=ip)
app.add_url_rule("/post", view_func=post, methods=("POST",))
app.add_url_rule("/ua", view_func=ua)
app.add_url_rule("/headers", view_func=headers)
app.add_url_rule(
    "/v1/pf-init", endpoint="v1_pf_init", view_func=v1.pf_init, methods=("GET",)
)
app.add_url_rule("/v1/pf", endpoint="v1_pf_get", view_func=v1.pf_get, methods=("GET",))
app.add_url_rule(
    "/v1/pf", endpoint="v1_pf_post", view_func=v1.pf_post, methods=("POST",)
)
app.add_url_rule(
    "/v1/pf", endpoint="v1_pf_delete", view_func=v1.pf_delete, methods=("DELETE",)
)
app.add_url_rule(
    "/v1/healthcheck",
    endpoint="v1_healthcheck",
    view_func=v1.healthcheck,
    methods=("GET",),
)
app.add_url_rule("/v2/pf", endpoint="v2_pf_get", view_func=v2.pf_get, methods=("GET",))
app.add_url_rule(
    "/v2/healthcheck",
    endpoint="v2_healthcheck",
    view_func=v2.healthcheck,
    methods=("GET",),
)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
