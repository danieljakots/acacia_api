#!/usr/bin/env python3

from flask import Flask

from api import v1_pf
from api import v2_pf
from api import misc

app = Flask(__name__)


app.add_url_rule("/", view_func=misc.hello)
app.add_url_rule("/ip", view_func=misc.ip)
app.add_url_rule("/ua", view_func=misc.ua)
app.add_url_rule(
    "/v1/pf-init", endpoint="v1_pf_init", view_func=v1_pf.pf_init, methods=("GET",)
)
app.add_url_rule("/v1/pf", endpoint="v1_pf_get", view_func=v1_pf.pf_get, methods=("GET",))
app.add_url_rule(
    "/v1/pf", endpoint="v1_pf_post", view_func=v1_pf.pf_post, methods=("POST",)
)
app.add_url_rule(
    "/v1/pf", endpoint="v1_pf_delete", view_func=v1_pf.pf_delete, methods=("DELETE",)
)
app.add_url_rule("/v2/pf", endpoint="v2_pf_get", view_func=v2_pf.pf_get, methods=("GET",))
app.add_url_rule(
    "/v2/healthcheck",
    endpoint="v2_healthcheck",
    view_func=v2_pf.healthcheck,
    methods=("GET",),
)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
