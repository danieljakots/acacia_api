#!/usr/bin/env python3

from flask import jsonify, request, make_response

from api import tools


@tools.require_auth
def pf_get():
    order = request.args.get("order")
    if order and order.lower() != "ip":
        return make_response(jsonify({"error": "Bad Request"}), 400)
    if order and order.lower() == "ip":
        order = "ip"
    results = tools.ip_get(order=order)
    IP_count = len(results)
    results = {"count": IP_count, "IP": results}
    return jsonify(results)


def healthcheck():
    results = tools.ip_count()
    if results < 3:
        return make_response(jsonify({"error": "Too few results, check health"}), 500)
    return jsonify("OK")
