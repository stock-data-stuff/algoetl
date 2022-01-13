#!/usr/bin/env bash

# This is meant to be run from within the container.

SCRIPT_DIR=$(cd `dirname $0` && pwd)

cd ${SCRIPT_DIR}

# These are set by the Docker environment variable setup
# $POSTGRES_DB, $POSTGRES_USER, $POSTGRES_PASSWORD

DIR_IN_PATH=/usr/local/bin
PSQL=${DIR_IN_PATH}/psql2

setup_psql() {
    # hostname:port:database:username:password
    echo "localhost:5432:$POSTGRES_DB:$POSTGRES_USER:$POSTGRES_PASSWORD" > ~/.pgpass
    chmod 700 ~/.pgpass

    # The above will allow this to work without a password
    # This works because pg_hba.conf is set up with 'trust' authentication.
    # psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB
    echo 'psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB $@' > $PSQL
    chmod 700 $PSQL

    echo "Show the defaul connection (db and user) when using: $PSQL"
    echo "\c" | $PSQL
}

run_sql_scripts() {
    for i in $(ls -1 ./setup/*.sql); do
	echo "run $i"
	cat $i | $PSQL
    done
}

setup_psql
run_sql_scripts
