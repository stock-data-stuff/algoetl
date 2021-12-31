.PHONY=all clean start status

# Force make to run targets sequentially
.NOTPARALLEL:

# Directory containing this makefile. Includes trailing /
MAKEFILE_PATH=$(dir $(realpath $(firstword $(MAKEFILE_LIST))))

# Set default shell as bash
# This is necessary because we use "source" below
SHELL:=/bin/bash

# Some script commands
START_DOCKER=$(shell ./run -u)
STOP_DOCKER=$(shell ./run -d)
PURGE_DOCKER=$(shell ./run -c)
DOCKER_STATUS=$(shell ./run -s)
DOCKER_LOGIN=$(shell ./run -l)
PYSPARK=$(shell ./run -p)

all: start

clean:
	$(info Clean)
	$(STOP_DOCKER)

clean-all:
	$(info Clean All)
	$(PURGE_DOCKER)

login:
	$(info Log into master node)
	$(DOCKER_LOGIN)

status:
	$(info Show docker status)
	$(DOCKER_SATUS)

pyspark:
	$(info Run Pyspark on master node)
	$(PYSPARK)

start:
	$(info Run)
	$(START_DOCKER)
	$(DOCKER_STATUS)

