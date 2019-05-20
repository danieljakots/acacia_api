#!/usr/bin/env python3

import json
import sys

import requests

API = "https://api.chown.me"
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


def get(shouldbe_data, order=None, rcode=200):
    if order:
        params = {"order": order}
    else:
        params = {}
    get = requests.get(f"{API}/v1/pf", headers=HEADERS, params=params, auth=IDENT)
    if get.status_code != rcode:
        print("GET bad status code")
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
        print("GET OK")


def post(data, rcode, msg):
    post = requests.post(f"{API}/v1/pf", headers=HEADERS, data=data, auth=IDENT)
    if post.status_code != rcode:
        print(f"{msg} bad status code")
        print(post.text)
        print(post.status_code)
        sys.exit(1)
    print(f"{msg} OK", end='... ')


def delete(data, rcode, msg):
    post = requests.delete(f"{API}/v1/pf", headers=HEADERS, data=data, auth=IDENT)
    if post.status_code != rcode:
        print(f"{msg} bad status code")
        sys.exit(1)
    print(f"{msg} OK", end='... ')


def main():
    init()
    shouldbe_data = '[["209.229.0.0/16"], ["219.229.0.2/32"]]'
    get(shouldbe_data)

    # missing source IP
    data = '[{"IP": "1.1.1.1"}, {"IP": "2.2.2.2"}]'
    rcode = 400
    msg = "BAD DATA"
    post(data, rcode, msg)
    shouldbe_data = '[["209.229.0.0/16"], ["219.229.0.2/32"]]'
    get(shouldbe_data)

    # good stuff
    data = '[{"IP": "1.1.1.1", "source": "test"}, {"IP": "2.2.2.2", "source": "test"}]'
    rcode = 204
    msg = "GOOD DATA"
    post(data, rcode, msg)
    shouldbe_data = (
        '[["209.229.0.0/16"], ["219.229.0.2/32"], ["1.1.1.1/32"], ["2.2.2.2/32"]]'
    )
    get(shouldbe_data)

    # good stuff again
    data = '[{"IP": "1.1.1.1", "source": "test"}, {"IP": "2.2.2.2", "source": "test"}]'
    rcode = 200
    msg = "GOOD DATA AGAIN"
    post(data, rcode, msg)
    shouldbe_data = (
        '[["209.229.0.0/16"], ["219.229.0.2/32"], ["1.1.1.1/32"], ["2.2.2.2/32"]]'
    )
    get(shouldbe_data)

    # both good and already given
    data = '[{"IP": "3.3.3.3", "source": "test"}, {"IP": "2.2.2.2", "source": "test"}]'
    rcode = 204
    msg = "GOOD DATA + ALREADY GIVEN DATA"
    post(data, rcode, msg)
    shouldbe_data = '[["209.229.0.0/16"], ["219.229.0.2/32"], ["1.1.1.1/32"], ["2.2.2.2/32"], ["3.3.3.3/32"]]'
    get(shouldbe_data)

    # both good and already given but reverse order
    data = '[{"IP": "2.2.2.2", "source": "test"}, {"IP": "4.4.4.4", "source": "test"}]'
    rcode = 204
    msg = "ALREADY GIVEN DATA + GOOD DATA"
    post(data, rcode, msg)
    shouldbe_data = '[["209.229.0.0/16"], ["219.229.0.2/32"], ["1.1.1.1/32"], ["2.2.2.2/32"], ["3.3.3.3/32"], ["4.4.4.4/32"]]'
    get(shouldbe_data)

    # only already given
    data = '[{"IP": "3.3.3.3", "source": "test"}, {"IP": "2.2.2.2", "source": "test"}]'
    rcode = 200
    msg = "ALREADY GIVEN DATA"
    post(data, rcode, msg)
    shouldbe_data = '[["209.229.0.0/16"], ["219.229.0.2/32"], ["1.1.1.1/32"], ["2.2.2.2/32"], ["3.3.3.3/32"], ["4.4.4.4/32"]]'
    get(shouldbe_data)

    # delete
    data = '[{"IP": "3.3.3.3"}, {"IP": "2.2.2.2"}]'
    rcode = 204
    msg = "DELETE DATA"
    delete(data, rcode, msg)
    shouldbe_data = '[["209.229.0.0/16"], ["219.229.0.2/32"], ["1.1.1.1/32"], ["4.4.4.4/32"]]'
    get(shouldbe_data)

    # get bad order
    print("GET BAD ORDERED DATA", end="... ")
    shouldbe_data = '{"error": "Bad Request"}'
    get(shouldbe_data, order="lol-IP", rcode=400)

    # get good order
    print("GET GOOD ORDERED DATA", end="... ")
    shouldbe_data = '[["1.1.1.1/32"], ["4.4.4.4/32"], ["209.229.0.0/16"], ["219.229.0.2/32"]]'
    get(shouldbe_data, order="IP")
    print("FINISHED")


if __name__ == "__main__":
    main()
