#!/usr/bin/env python3

from flask import jsonify, request

from api import tools


def hello():
    return jsonify("Hello world!")


def ip():
    return jsonify(origin=request.headers.get("X-Forwarded-For", request.remote_addr))


def ua():
    headers = dict(request.headers.items())
    return jsonify({"User-Agent": headers["User-Agent"]})
