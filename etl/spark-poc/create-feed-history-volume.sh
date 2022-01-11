#!/bin/bash

# Create a Docker External Volume
#   DOCKER_VOLUME_ID: the Docker volume ID/Name
#   FEED_HISTORY_DIR: the path on the local host with the data.
#
# If FEED_HISTORY_DIR is not given, find the path relative to this script.


DOCKER_VOLUME_ID="feed_history"
echo "DOCKER_VOLUME_ID, the name of the Docker Volume, is: ${DOCKER_VOLUME_ID}"

# Uncomment this to always recreate the volume
docker volume rm "${DOCKER_VOLUME_ID}"


if [ -n "$FEED_HISTORY_DIR" ]; then
    echo "Environment variable FEED_HISTORY_DIR is set. Using: ${FEED_HISTORY_DIR}"
    FEED_HISTORY_DIR=$(cd "$FEED_HISTORY_DIR" && pwd)
else
    SCRIPT_DIR=$(dirname $(realpath $0 ))
    FEED_HISTORY_DIR=$(cd ${SCRIPT_DIR}/../../feed-history && pwd)
fi
echo "FEED_HISTORY_DIR, the directory on the OS, is: ${FEED_HISTORY_DIR}"


if docker volume inspect ${DOCKER_VOLUME_ID} >/dev/null; then
    echo "Docker Volume already exists. Not recreating it."
else
    echo "Docker Volume does not already exist. Creating it."
    docker volume create --driver local \
           --opt type=volume \
           --opt device=${FEED_HISTORY_DIR} \
           --opt o=bind ${DOCKER_VOLUME_ID}
fi

echo "Showing information on the volume"

docker volume inspect ${DOCKER_VOLUME_ID}
