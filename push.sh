#!/bin/sh

set -eux

_REGISTRY=r.chown.me
_IMAGE=api

docker build . -t ${_IMAGE}:$(git last)-$(date +%F)
docker tag ${_IMAGE}:$(git last)-$(date +%F) ${_REGISTRY}/${_IMAGE}:$(git last)-$(date +%F)
docker push ${_REGISTRY}/${_IMAGE}:$(git last)-$(date +%F)
echo "${_REGISTRY}/${_IMAGE}:$(git last)-$(date +%F)"
