#!/usr/bin/env sh

if [ -z "$IMAGE_TAG" ]; then
    echo "No IMAGE_TAG set in environment. Set IMAGE_TAG environment variable."
    exit 1
fi

docker build -t $IMAGE_TAG .
echo "$DOCKER_PASS" | docker login -u $DOCKER_USER --password-stdin
docker push $IMAGE_TAG