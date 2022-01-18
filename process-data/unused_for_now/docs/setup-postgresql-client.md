# GOAL

Document how I set up the postgresql client

## Install postgresql client (and db, just in case we want to use it)

sudo apt install postgresql postgresql-contrib

Gave me this response.
Success. You can now start the database server using:
 pg_ctlcluster 13 main start

## Confirm PG is listening locally (from its docker container)

sudo netstat -tulpn  | grep 5432
tcp        0      0 0.0.0.0:5432            0.0.0.0:*               LISTEN      304782/docker-proxy
tcp6       0      0 :::5432                 :::*                    LISTEN      304788/docker-proxy

## Check the postgresql credentials

cat ./postgresql/postgresql.env

## Put the parameters in ~/.pgpass

Contents should be
# hostname:port:database:username:password
127.0.0.1:5432:test:testuser:TestUser1!

chmod 0600 ~/.pgpass
