.PHONY=all clean status up login test

# Force make to run targets sequentially
.NOTPARALLEL:

# Directory containing this makefile. Includes trailing /
MAKEFILE_PATH=$(dir $(realpath $(firstword $(MAKEFILE_LIST))))

all: run

clean:
	$(info Clean)
	./run -c

status:
	$(info Show docker status)
	./run -s

up:
	$(info Running docker-compose up)
	./run -u

login: up
	$(info Log into Postgres node)
	./run -l

test: up
	$(info Run a test of the DB)
	./run -t

