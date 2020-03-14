#!/bin/sh

docker build /home/danj/git/git.chown.me/api -t api:latest

export PGPASSWORD_POSTGRES=hunter2
export PGPASSWORD_API=hunter3

_DOCKER_NET=mynet
_PG_CONTAINER=pgdocker
_API_VERSION=latest
_PG_VERSION=12.2

[ $(docker ps -a | grep -c "$_PG_CONTAINER") -gt 0 ] && echo "cleaning pgsql" && \
	docker rm --force "$_PG_CONTAINER" > /dev/null
[ $(docker ps -a | grep -c api) -gt 0 ] && echo "cleaning api" && \
	docker rm --force api > /dev/null
[ $(docker network ls | grep -c "$_DOCKER_NET") -gt 0 ] && \
	echo "cleaning network" && docker network rm "$_DOCKER_NET" > /dev/null

[ ${1:-nah} = "stop" ] && exit 0

set -e

echo "creating network"
docker network create "$_DOCKER_NET"
echo "creating postgres"
docker run -d --rm --name "$_PG_CONTAINER" --net "$_DOCKER_NET" -p 5432:5432 \
	-e POSTGRES_PASSWORD=$PGPASSWORD_POSTGRES \
	postgres:"$_PG_VERSION" -c 'shared_buffers=512MB'

set +e
while true
do
	docker exec -it -e PGPASSWORD=$PGPASSWORD_POSTGRES \
		"$_PG_CONTAINER" pg_isready
	[ $? -eq 0 ] && break
	sleep 0.01
done
set -e

echo "initializing postgres"
docker exec -it -e PGPASSWORD=$PGPASSWORD_POSTGRES "$_PG_CONTAINER" createuser -U postgres --no-password api
docker exec -it -e PGPASSWORD=$PGPASSWORD_POSTGRES "$_PG_CONTAINER" psql -U postgres -c \
	"ALTER USER api WITH PASSWORD '$PGPASSWORD_API';"
docker exec -it -e PGPASSWORD=$PGPASSWORD_POSTGRES "$_PG_CONTAINER" createdb -U postgres -O api api
docker exec -it -e PGPASSWORD=$PGPASSWORD_API "$_PG_CONTAINER" psql -d api -U api -c \
	'CREATE TABLE users (api_user character varying UNIQUE, password character varying, active INTEGER);'
docker exec -it -e PGPASSWORD=$PGPASSWORD_API "$_PG_CONTAINER" psql -d api -U api -c \
	'ALTER TABLE users OWNER TO api;'
docker exec -it -e PGPASSWORD=$PGPASSWORD_API "$_PG_CONTAINER" psql -d api -U api -c \
	"INSERT INTO users VALUES ('test', '8d604831', 1);"

echo "creating api"
docker run -d --rm -p 8123:8123 --name api --net "$_DOCKER_NET" \
	-e PG_HOST="$_PG_CONTAINER" -e PG_PASSWORD=$PGPASSWORD_API -e PG_USER=api -e PG_DB=api \
	--mount type=tmpfs,destination=/tmpfs,tmpfs-mode=777,tmpfs-size=32M api:"$_API_VERSION"

echo -n "waiting for api"
set +e
while true
do
	[ $(curl -s localhost:8123/ | grep -c "Hello world") -eq 1 ] && break
	sleep 0.1
	echo -n "."
done
set -e

echo -e "\nrunning regress test"
python3 regress.py
