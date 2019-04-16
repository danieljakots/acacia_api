#!/usr/bin/env python3

import json
import sys

import requests

API = "https://api.chown.me"
HEADERS = {"key": "blih", "User-Agent": "meh", "Content-Type": "application/json"}


def init():
    get = requests.get(f"{API}/v1/pf-init", headers=HEADERS)
    if get.status_code != 204:
        print("INIT bad status code")
        sys.exit(1)


def get(shouldbe_data):
    get = requests.get(f"{API}/v1/pf", headers=HEADERS)
    if get.status_code != 200:
        print("GET bad status code")
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
    post = requests.post(f"{API}/v1/pf", headers=HEADERS, data=data)
    if post.status_code != rcode:
        print(f"{msg} bad status code")
        print(post.text)
        print(post.status_code)
        sys.exit(1)
    print(f"{msg} OK", end='... ')


def delete():
    data = '[{"IP": "1.1.1.1"}, {"IP": "2.2.2.2"}]'
    post = requests.delete(f"{API}/v1/pf", headers=HEADERS, data=data)
    if post.status_code != 204:
        print("DELETE bad status code")
        sys.exit(1)
    print("DELETE OK")


def main():
    init()
    shouldbe_data = '[["209.229.0.0/16"], ["219.229.0.2/32"]]'
    get(shouldbe_data)

    data = '[{"IP": "1.1.1.1"}, {"IP": "2.2.2.2"}]'
    rcode = 400
    msg = "BAD DATA"
    post(data, rcode, msg)
    shouldbe_data = '[["209.229.0.0/16"], ["219.229.0.2/32"]]'
    get(shouldbe_data)

    data = '[{"IP": "1.1.1.1", "source": "test"}, {"IP": "2.2.2.2", "source": "test"}]'
    rcode = 204
    msg = "GOOD DATA"
    post(data, rcode, msg)
    shouldbe_data = (
        '[["209.229.0.0/16"], ["219.229.0.2/32"], ["1.1.1.1/32"], ["2.2.2.2/32"]]'
    )
    get(shouldbe_data)

    data = '[{"IP": "1.1.1.1", "source": "test"}, {"IP": "2.2.2.2", "source": "test"}]'
    rcode = 200
    msg = "GOOD DATA AGAIN"
    post(data, rcode, msg)
    shouldbe_data = (
        '[["209.229.0.0/16"], ["219.229.0.2/32"], ["1.1.1.1/32"], ["2.2.2.2/32"]]'
    )
    get(shouldbe_data)

    data = '[{"IP": "3.3.3.3", "source": "test"}, {"IP": "2.2.2.2", "source": "test"}]'
    rcode = 204
    msg = "GOOD DATA + ALREADY GIVEN DATA"
    post(data, rcode, msg)
    shouldbe_data = '[["209.229.0.0/16"], ["219.229.0.2/32"], ["1.1.1.1/32"], ["2.2.2.2/32"], ["3.3.3.3/32"]]'
    get(shouldbe_data)

    data = '[{"IP": "2.2.2.2", "source": "test"}, {"IP": "4.4.4.4", "source": "test"}]'
    rcode = 204
    msg = "ALREADY GIVEN DATA + GOOD DATA"
    post(data, rcode, msg)
    shouldbe_data = '[["209.229.0.0/16"], ["219.229.0.2/32"], ["1.1.1.1/32"], ["2.2.2.2/32"], ["3.3.3.3/32"], ["4.4.4.4/32"]]'
    get(shouldbe_data)

    data = '[{"IP": "3.3.3.3", "source": "test"}, {"IP": "2.2.2.2", "source": "test"}]'
    rcode = 200
    msg = "ALREADY GIVEN DATA"
    post(data, rcode, msg)
    shouldbe_data = '[["209.229.0.0/16"], ["219.229.0.2/32"], ["1.1.1.1/32"], ["2.2.2.2/32"], ["3.3.3.3/32"], ["4.4.4.4/32"]]'
    get(shouldbe_data)


if __name__ == "__main__":
    main()
