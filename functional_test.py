#!/usr/bin/env python3

import json
import sys

import requests

API = "https://api.chown.me"


def test_get(shouldbe_data):
    headers = {"key": "blih", "User-Agent": "meh"}
    get = requests.get(f"{API}/v1/pf", headers=headers)
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


def test_no_post():
    headers = {"key": "blih", "Content-Type": "application/json"}
    data = '[{"IP": "1.1.1.1"}, {"IP": "2.2.2.2"}]'
    post = requests.post(f"{API}/v1/pf", headers=headers, data=data)
    if post.status_code != 400:
        print("NO POST bad status code")
        sys.exit(1)
    print("NO POST OK")


def test_post():
    headers = {"key": "blih", "Content-Type": "application/json"}
    data = '[{"IP": "1.1.1.1", "source": "test"}, {"IP": "2.2.2.2", "source": "test"}]'
    post = requests.post(f"{API}/v1/pf", headers=headers, data=data)
    if post.status_code != 204:
        print("POST bad status code")
        sys.exit(1)
    print("POST OK")


def test_delete():
    headers = {"key": "blih", "Content-Type": "application/json"}
    data = '[{"IP": "1.1.1.1"}, {"IP": "2.2.2.2"}]'
    post = requests.delete(f"{API}/v1/pf", headers=headers, data=data)
    if post.status_code != 204:
        print("DELETE bad status code")
        sys.exit(1)
    print("DELETE OK")


def main():
    print("BEGIN TEST_GET")
    shouldbe_data = '[["209.229.0.0/16"], ["219.229.0.2/32"]]'
    test_get(shouldbe_data)
    print("BEGIN TEST_NO_POST")
    test_no_post()
    print("BEGIN TEST_POST")
    test_post()
    print("BEGIN TEST_GET AGAIN")
    shouldbe_data = (
        '[["209.229.0.0/16"], ["219.229.0.2/32"], ["1.1.1.1/32"], ["2.2.2.2/32"]]'
    )
    test_get(shouldbe_data)
    print("BEGIN TEST_DELETE")
    test_delete()
    print("BEGIN TEST_GET LAST")
    shouldbe_data = '[["209.229.0.0/16"], ["219.229.0.2/32"]]'
    test_get(shouldbe_data)


if __name__ == "__main__":
    main()
