.PHONY=all clean status up login test clean-all

# Force make to run targets sequentially
.NOTPARALLEL:

# Directory containing this makefile. Includes trailing /
MAKEFILE_PATH=$(dir $(realpath $(firstword $(MAKEFILE_LIST))))

all: test

clean:
	$(info Clean)
	./run -c

clean-all: clean
	$(info Clean all files)
	sudo rm -rf ../../postgres-data

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

