#!/bin/sh

export PGPASSWORD=hunter2

_DOCKER_NET=mynet
_PG_CONTAINER=pgdocker
_API_VERSION=14
_PG_VERSION=12.2

[ $(docker ps -a | grep -c "$_PG_CONTAINER") -gt 0 ] && echo "cleaning pgsql" && \
	docker rm --force "$_PG_CONTAINER" > /dev/null
[ $(docker ps -a | grep -c api) -gt 0 ] && echo "cleaning api" && \
	docker rm --force api > /dev/null
[ $(docker network ls | grep -c "$_DOCKER_NET") -gt 0 ] && \
	echo "cleaning network" && docker network rm "$_DOCKER_NET" > /dev/null

set -e

echo "creating network"
docker network create "$_DOCKER_NET"
echo "creating postgres"
docker run -d --rm --name "$_PG_CONTAINER" --net "$_DOCKER_NET" -p 5432:5432 \
	-e POSTGRES_USER=api -e POSTGRES_PASSWORD=$PGPASSWORD \
	postgres:"$_PG_VERSION" -c 'shared_buffers=512MB'

sleep 3

echo "initializing postgres"
docker exec -it -e PGPASSWORD=$PGPASSWORD "$_PG_CONTAINER" psql -d api -U api -c \
	'CREATE TABLE users (api_user character varying UNIQUE, password character varying, active INTEGER);'
docker exec -it -e PGPASSWORD=$PGPASSWORD "$_PG_CONTAINER" psql -d api -U api -c \
	'ALTER TABLE users OWNER TO api;'
docker exec -it -e PGPASSWORD=$PGPASSWORD "$_PG_CONTAINER" psql -d api -U api -c \
	"INSERT INTO users VALUES ('test', '8d604831', 1);"

sleep 1

echo "creating api"
docker run -d --rm -p 8123:8123 --name api --net "$_DOCKER_NET" \
	-e PG_HOST="$_PG_CONTAINER" -e PG_PASSWORD=$PGPASSWORD -e PG_USER=api -e PG_DB=api \
	--mount type=tmpfs,destination=/tmpfs,tmpfs-mode=777,tmpfs-size=32M api:"v$_API_VERSION"

sleep 2

echo "running regress test"
python3 regress.py
