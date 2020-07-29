#!/usr/bin/env sh
echo "$DOCKER_PASS" | docker login -u "${DOCKER_USER}" --password-stdin

if [ "${TRAVIS_BRANCH}" = "master" ]; then
    TAG="latest"
    docker tag "${IMAGE}" "${IMAGE}:${TAG}"
    docker push "${IMAGE}:${TAG}"
fi

if [ -n "${TRAVIS_TAG}" ]; then
    TAG="${TRAVIS_TAG}"
    docker tag "${IMAGE}" "${IMAGE}:${TAG}"
    docker push "${IMAGE}:${TAG}"
fi
