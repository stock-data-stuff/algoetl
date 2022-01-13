#!/usr/bin/env bash

# This is meant to be run from the host.
# It expects docker-compose to be configured.

SCRIPT_DIR=$(cd `dirname $0` && pwd)
source ${SCRIPT_DIR}/../postgresql.env

# Wait until the postgres "pg_isready" command says the DB allowed a particular user to connect
check_isready() {
  for i in {1..50}; do
    if docker-compose exec postgresdb bash -c "pg_isready -U $POSTGRES_USER"; then
      echo "pg_isready reports it is ready"
      return
    fi
    sleep 0.2
  done
  echo "ERROR: Health Check failed"
  exit 1
}

check_isready

docker-compose exec postgresdb bash -c "cd /scripts && ./run-setup-from-within-container.sh"
