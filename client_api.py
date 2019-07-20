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


def get_pf_table_list():
    command = subprocess.run(
        ["doas", "pfctl", "-ST"], stdout=subprocess.PIPE, encoding="utf-8"
    )
    for line in command.stdout.split():
        if line[:5] == "brute":
            yield line


def get_pf_table_content(table):
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
    if post.status_code != 204:
        print(f"POST bad status code: {post.status_code}")
        sys.exit(1)


def get_api_bans(IP):
    get = requests.post(f"{API}/v1/pf", auth=IDENT)
    if get.status_code != 200:
        print(f"GET bad status code: {get.status_code}")
        sys.exit(1)
    # json will be [['209.229.0.0/16'], ['219.229.0.2/32']]
    for field in get.json():
        yield(field[0])



def feed_pf_table(address):
    subprocess.run(
        ["doas", "pfctl", "-t", "api_bans", "-Ta", address],
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )


def main():
    emerging = get_emerging_threats()
    IP = parse_emerging(emerging)
    feed_api(IP)

    for table in get_pf_table_list():
        IP = get_pf_table_content(table)
        feed_api(IP)


if __name__ == "__main__":
    main()
