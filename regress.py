#!/usr/bin/env python3

import json
import sys

import requests

API = "http://localhost:8123"
HEADERS = {"Content-Type": "application/json"}
IDENT = ("test", "8d604831")


def init():
    get = requests.get(f"{API}/v1/pf-init", headers=HEADERS, auth=IDENT)
    rcode = 204
    if get.status_code != rcode:
        print("INIT bad status code")
        print(f"got {get.status_code}, should have been {rcode}")
        print(get.text)
        sys.exit(1)
    print("INIT OK")


def get(shouldbe_data, order=None, rcode=200, version=1):
    if order:
        params = {"order": order}
    else:
        params = {}
    get = requests.get(f"{API}/v{version}/pf", headers=HEADERS, params=params,
                       auth=IDENT)
    if get.status_code != rcode:
        print(f"GET v{version} bad status code")
        print(f"got {get.status_code}, should have been {rcode}")
        print(get.text)
        sys.exit(1)
    shouldbe_json = json.loads(shouldbe_data)
    if get.json() != shouldbe_json:
        print("we got")
        print(get.json())
        print("expected")
        print(shouldbe_json)
        sys.exit(1)
    else:
        print(f"GET v{version} OK")


def post(data, rcode, msg):
    post = requests.post(f"{API}/v1/pf", headers=HEADERS, data=data, auth=IDENT)
    if post.status_code != rcode:
        print(f"POST {msg} bad status code")
        print(f"got {post.status_code}, should have been {rcode}")
        print(post.text)
        sys.exit(1)
    print(f"{msg} OK", end='... ')


def delete(data, rcode, msg):
    delete = requests.delete(f"{API}/v1/pf", headers=HEADERS, data=data, auth=IDENT)
    if delete.status_code != rcode:
        print(f"{msg} bad status code")
        sys.exit(1)
    print(f"{msg} OK", end='... ')


def health(rcode, msg):
    get = requests.get(f"{API}/v2/healthcheck", headers=HEADERS, auth=IDENT)
    if get.status_code != rcode:
        print(f"HEALTH bad status code")
        print(f"got {get.status_code}, should have been {rcode}")
        print(get.text)
        sys.exit(1)
    if get.text != msg:
        print("we got")
        print(get.text)
        print("expected")
        print(msg)
        sys.exit(1)
    else:
        print(f"HEALTH OK")


def test_ident():
    get = requests.get(f"{API}/v1/pf", headers=HEADERS, auth=("bad", "credentials"))
    rcode = 500
    if get.status_code != rcode:
        print(f"IDENT bad status code")
        print(f"got {get.status_code}, should have been {rcode}")
        sys.exit(1)
    print("IDENT OK")


def main():
    init()

    health(200, '"OK"\n')
    data = '[{"IP": "203.0.113.123"}, {"IP": "192.0.2.24"}]'
    rcode = 204
    msg = "DELETE DATA"
    delete(data, rcode, msg)
    health(500, '{"error":"Too few results, check health"}\n')

    # shouldbe
    shouldbe_data = '[["198.51.100.0/26"], ["198.51.100.212/32"]]'
    get(shouldbe_data)

    # missing source IP
    data = '[{"IP": "192.0.2.1"}, {"IP": "203.0.113.253"}]'
    rcode = 400
    msg = "BAD DATA"
    post(data, rcode, msg)
    shouldbe_data = '[["198.51.100.0/26"], ["198.51.100.212/32"]]'
    get(shouldbe_data)

    # good stuff
    data = '[{"IP": "192.0.2.1", "source": "test"}, {"IP": "203.0.113.253", "source": "test"}]'
    rcode = 204
    msg = "GOOD DATA"
    post(data, rcode, msg)
    shouldbe_data = (
        '[["198.51.100.0/26"], ["198.51.100.212/32"], ["192.0.2.1/32"], ["203.0.113.253/32"]]'
    )
    get(shouldbe_data)

    # good stuff again
    data = '[{"IP": "192.0.2.1", "source": "test"}, {"IP": "203.0.113.253", "source": "test"}]'
    rcode = 204
    msg = "GOOD DATA AGAIN"
    post(data, rcode, msg)
    shouldbe_data = (
        '[["198.51.100.0/26"], ["198.51.100.212/32"], ["192.0.2.1/32"], ["203.0.113.253/32"]]'
    )
    get(shouldbe_data)

    # both good and already given
    data = '[{"IP": "203.0.113.42", "source": "test"}, {"IP": "203.0.113.253", "source": "test"}]'
    rcode = 204
    msg = "GOOD DATA + ALREADY GIVEN DATA"
    post(data, rcode, msg)
    shouldbe_data = '[["198.51.100.0/26"], ["198.51.100.212/32"], ["192.0.2.1/32"],' \
        '["203.0.113.253/32"], ["203.0.113.42/32"]]'
    get(shouldbe_data)

    # both good and already given but reverse order
    data = '[{"IP": "203.0.113.253", "source": "test"}, {"IP": "198.51.100.57", "source": "test"}]'
    rcode = 204
    msg = "ALREADY GIVEN DATA + GOOD DATA"
    post(data, rcode, msg)
    shouldbe_data = '[["198.51.100.0/26"], ["198.51.100.212/32"], ["192.0.2.1/32"],' \
        '["203.0.113.253/32"], ["203.0.113.42/32"], ["198.51.100.57/32"]]'
    get(shouldbe_data)

    # only already given
    data = '[{"IP": "203.0.113.42", "source": "test"}, {"IP": "203.0.113.253", "source": "test"}]'
    rcode = 204
    msg = "ALREADY GIVEN DATA"
    post(data, rcode, msg)
    shouldbe_data = '[["198.51.100.0/26"], ["198.51.100.212/32"], ["192.0.2.1/32"],' \
        '["203.0.113.253/32"], ["203.0.113.42/32"], ["198.51.100.57/32"]]'
    get(shouldbe_data)

    # delete
    data = '[{"IP": "203.0.113.42"}, {"IP": "203.0.113.253"}]'
    rcode = 204
    msg = "DELETE DATA"
    delete(data, rcode, msg)
    shouldbe_data = '[["198.51.100.0/26"], ["198.51.100.212/32"], ["192.0.2.1/32"],'\
        '["198.51.100.57/32"]]'
    get(shouldbe_data)

    # get bad order
    print("GET v1 BAD ORDERED DATA", end="... ")
    shouldbe_data = '{"error": "Bad Request"}'
    get(shouldbe_data, order="lol-IP", rcode=400)

    # get good order
    print("GET v1 GOOD ORDERED DATA", end="... ")
    shouldbe_data = '[["192.0.2.1/32"], ["198.51.100.0/26"], ["198.51.100.57/32"],'\
        '["198.51.100.212/32"]]'
    get(shouldbe_data, order="IP")

    # Test with bad credentials
    test_ident()

    print("FINISHED")

if __name__ == "__main__":
    main()
