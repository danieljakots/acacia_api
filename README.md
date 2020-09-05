# acacia_api

This is a basic REST API to store IP addresses in PostgreSQL.
A client is provided: `acacia_client.j2` (note that it can also interact with
*acacia_pubsub*).

# Installation

## With docker

The Dockerfile sets gunicorn's --worker-tmp-dir to a tmpfs to avoid problems.

```
$ docker run -d --rm -p 8123:8123 --name api -e PG_HOST=XXX -e PG_PASSWORD=XXX \
	-e PG_USER=api -e PG_DB=api \
	--mount type=tmpfs,destination=/tmpfs,tmpfs-mode=777,tmpfs-size=32M
	api:c5baf27-2020-08-30
```

## With docker-compose

```
$ cat .env.api
PG_HOST=10.10.10.1
PG_PASSWORD=hunter2
```

```
  api:
    image: r.chown.me/api:c5baf27-2020-08-30
    restart: "no"
    env_file: .env.api
    security_opt:
      - "no-new-privileges:true"
    cap_drop:
      - ALL
    tmpfs:
      - /tmpfs:mode=770,size=32M,uid=100,gid=100
    healthcheck:
      test: ["CMD-SHELL", "wget -q --spider localhost:8123/v2/healthcheck || exit 1"]
    ports:
      - "10.10.10.2:8123:8123"
```

# User management

You can't manage the users through the API, you need to do it with SQL
directly.

~~~
INSERT INTO USERS (api_user, password, active) VALUES ('machine.example.com', 'hunter2', 1);
~~~

# Usage

A client is provided:

~~~
$ acacia_client -h
usage: acacia_client [-h] [-q | -v] {add,delete,cron,count,extsources,list} ...

positional arguments:
  {add,delete,cron,count,extsources,list}
                        Type of action you want to do
    add                 Add a new IP
    delete              Delete an IP
    cron                Cron mode
    count               Count how many IP
    extsources          Add IP from external sources (emerging threats and blocklist dot de)
    list                List IP from api

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           Shut up
  -v, --verbose         Be verbose
~~~

To understand more about the whole thing, you can read my [blog
article](https://chown.me/blog/acacia).

# API documentation

| Endpoint        | Method | Bleh                                               |
|-----------------|--------|----------------------------------------------------|
| /v1/pf-init     | GET    | (Re)initialize table pf_ip_ban                     |
| /v1/pf          | GET    | Returns a json with all the IP listed in pf_ip_ban |
| /v1/pf          | POST   | Returns a 204 when the json is valid               |
| /v1/pf          | DELETE | Returns a 204 when the json is valid               |
| /v2/healthcheck | GET    | Returns "OK" if healthy                            |

## json examples

### v1/pf (get)

`
[
	["198.51.100.0/26"],
	["198.51.100.212/32"],
	["192.0.2.1/32"],
	["198.51.100.57/32"]
]
`

### v1/pf (post)

`
[{
	"IP": "192.0.2.1",
	"source": "test"
}, {
	"IP": "203.0.113.253",
	"source": "test"
}]
`

### v1/pf (delete)

`
[{
	"IP": "203.0.113.42"
}, {
	"IP": "203.0.113.253"
}]
`

# Development

There's a regress script (regress.py) to check api's functionality is working
as intended. The easiest way to do it is to run `ci.sh` script as it will setup
everything and you don't have anything to do. But you need docker.

