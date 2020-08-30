#!/usr/bin/env python3

from flask import jsonify, make_response

from api import tools


def healthcheck():
    results = tools.ip_count()
    if results < 3:
        return make_response(jsonify({"error": "Too few results, check health"}), 500)
    return jsonify("OK")
