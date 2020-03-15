#!/usr/bin/env python3

from flask import jsonify, request

from api import tools


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
