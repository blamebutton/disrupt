#!/usr/bin/env sh
echo "$DOCKER_PASS" | docker login -u $DOCKER_USER --password-stdin
docker push $IMAGE_TAG