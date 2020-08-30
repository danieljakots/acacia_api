#!/usr/bin/env python3

from flask import jsonify, request, make_response

from api import tools


@tools.require_auth
def pf_init():
    tools.ip_init()
    return ("", 204)


@tools.require_auth
def pf_get():
    order = request.args.get("order")
    if order and order.lower() != "ip":
        return make_response(jsonify({"error": "Bad Request"}), 400)
    if order and order.lower() == "ip":
        order = "ip"
    results = tools.ip_get(order=order)
    return jsonify(results)


@tools.require_auth
def pf_post():
    if request.form:
        post_data = request.form.to_dict()
        if "IP" not in post_data.keys() or "source" not in post_data.keys():
            return make_response(jsonify({"error": "Bad Request: key missing"}), 400)
        message, status_code = tools.ip_add(
            [{"IP": post_data["IP"], "source": post_data["source"]}]
        )
    elif request.json:
        (message, status_code) = tools.ip_add(request.get_json())
    else:
        return make_response(jsonify({"error": "Bad Request: not a form"}), 400)
    return (jsonify(message), status_code)


@tools.require_auth
def pf_delete():
    if request.json:
        data = request.get_json()
        for entry in data:
            try:
                IP = entry["IP"]
            except KeyError:
                return make_response(jsonify({"error": "Bad Request"}), 400)
            tools.ip_delete(IP)
    return ("", 204)
