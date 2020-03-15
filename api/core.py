#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response

from api import tools

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


@tools.require_auth
def v1_pf_init():
    tools.ip_init()
    return ("", 204)


@tools.require_auth
def v1_pf_get():
    order = request.args.get("order")
    if order and order.lower() != "ip":
        return make_response(jsonify({"error": "Bad Request"}), 400)
    if order and order.lower() == "ip":
        order = "ip"
    results = tools.ip_get(order=order)
    return jsonify(results)


@tools.require_auth
def v1_pf_post():
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
def v1_pf_delete():
    if request.json:
        data = request.get_json()
        for entry in data:
            try:
                IP = entry["IP"]
            except KeyError:
                return make_response(jsonify({"error": "Bad Request"}), 400)
            tools.ip_delete(IP)
    return ("", 204)


def v1_healthcheck():
    results = tools.ip_count()
    if results < 3:
        return make_response(jsonify({"error": "Too few results, check health"}), 500)
    return jsonify(results)


@tools.require_auth
def v2_pf_get():
    order = request.args.get("order")
    if order and order.lower() != "ip":
        return make_response(jsonify({"error": "Bad Request"}), 400)
    if order and order.lower() == "ip":
        order = "ip"
    results = tools.ip_get(order=order)
    IP_count = len(results)
    results = {"count": IP_count, "IP": results}
    return jsonify(results)


def v2_healthcheck():
    results = tools.ip_count()
    if results < 3:
        return make_response(jsonify({"error": "Too few results, check health"}), 500)
    return jsonify("OK")


app.add_url_rule("/", view_func=hello)
app.add_url_rule("/ip", view_func=ip)
app.add_url_rule("/post", view_func=post, methods=("POST",))
app.add_url_rule("/ua", view_func=ua,)
app.add_url_rule("/headers", view_func=headers)
app.add_url_rule("/v1/pf-init", view_func=v1_pf_init, methods=("GET",))
app.add_url_rule("/v1/pf", view_func=v1_pf_get, methods=("GET",))
app.add_url_rule("/v1/pf", view_func=v1_pf_post, methods=("POST",))
app.add_url_rule("/v1/pf", view_func=v1_pf_delete, methods=("DELETE",))
app.add_url_rule("/v1/healthcheck", view_func=v1_healthcheck, methods=("GET",))
app.add_url_rule("/v2/pf", view_func=v2_pf_get, methods=("GET",))
app.add_url_rule("/v2/healthcheck", view_func=v2_healthcheck, methods=("GET",))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
