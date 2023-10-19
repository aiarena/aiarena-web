#!/usr/bin/env bash
set -e

# Helper to run celery worker using /app as a current working directory
random_suffix=$(</dev/urandom tr -cd 'a-f0-9' | head -c 8)
queue=${!#//,/-}

export CELERY_WORKER_NAME="${queue}-${random_suffix}"
# https://stackoverflow.com/questions/20995351/docker-how-to-get-container-information-from-within-the-container
CONTAINER_ID=$(grep 'memory:/' < /proc/self/cgroup | sed 's|.*/||')
export CONTAINER_ID

celery="/usr/local/bin/celery-${random_suffix}"
ln -s /usr/local/bin/celery ${celery}

cd /app || exit 1
exec ${celery} $* -n ${CELERY_WORKER_NAME}
