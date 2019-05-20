#!/usr/bin/env python3

import datetime
import socket
import subprocess
import sys

import requests

API = "https://api.chown.me"
IDENT = ("test", "8d604831")


def now_to_strftime():
    now = datetime.datetime.now()
    return now.strftime("%Y/%m/%d %H:%M:%S")


def get_pf(table):
    hostname = socket.gethostname()
    timestamp = now_to_strftime()
    command = subprocess.run(
        ["doas", "pfctl", "-t", table, "-Ts"], stdout=subprocess.PIPE, encoding="utf-8"
    )
    IP = []
    for line in command.stdout.split():
        IP.append({"IP": line, "source": f"{timestamp} - {hostname}/{table}"})


def get_emerging_threats():
    g = requests.get("https://rules.emergingthreats.net/fwrules/emerging-Block-IPs.txt")
    return g.text


def parse_emerging(emerging):
    timestamp = now_to_strftime()
    IP = []
    for line in emerging.split("\n"):
        if not line or line[0] == "#":
            continue
        IP.append({"IP": line, "source": f"{timestamp} - emerging"})
    return IP


def feed_api(IP):
    headers = {"Content-Type": "application/json"}
    # yes it's needed
    data = str(IP).replace("'", '"')
    post = requests.post(f"{API}/v1/pf", headers=headers, data=data, auth=IDENT)
    print(post.text)
    print(post.status_code)
    if post.status_code != 204:
        print("POST bad status code")
        sys.exit(1)
    print("POST OK")


def main():
    emerging = get_emerging_threats()
    IP = parse_emerging(emerging)
    feed_api(IP)

    pf_tables = []
    for table in pf_tables:
        IP = get_pf(table)
        feed_api(IP)


if __name__ == "__main__":
    main()
