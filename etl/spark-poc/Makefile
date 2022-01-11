.PHONY=all clean start status

# Force make to run targets sequentially
.NOTPARALLEL:

# Directory containing this makefile. Includes trailing /
MAKEFILE_PATH=$(dir $(realpath $(firstword $(MAKEFILE_LIST))))

# Set default shell as bash
# This is necessary because we use "source" below
SHELL:=/bin/bash

all: start

clean:
	$(info Clean)
	./run -d

clean-all:
	$(info Clean All)
	./run -c

login:
	$(info Log into master node)
	./run -l

status:
	$(info Show docker status)
	./run -s

pyspark:
	$(info Run Pyspark on master node)
	./run -p

start:
	$(info Run)
	./run -u
	sleep 3
	./run -s


