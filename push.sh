#!/bin/sh

set -eux

docker build . -t api:$(git last)-$(date +%F)
# DOCKER_UPLOAD api:$(git last)-$(date +%F)
docker tag api:$(git last)-$(date +%F) r.chown.me/api:$(git last)-$(date +%F)
docker push r.chown.me/api:$(git last)-$(date +%F)
echo "r.chown.me/api:$(git last)-$(date +%F)"
