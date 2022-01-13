.PHONY=all clean clean-all run get process

# Force make to run targets sequentially
.NOTPARALLEL:

# Directory containing this makefile. Includes trailing /
MAKEFILE_PATH=$(dir $(realpath $(firstword $(MAKEFILE_LIST))))

# Set default shell as bash
SHELL:=/bin/bash

all: clean run

# stop services
clean:
	cd $(MAKEFILE_PATH)/get-data && make clean
	cd $(MAKEFILE_PATH)/process-data && make clean

# Aggressively remove files
clean-all:
	cd $(MAKEFILE_PATH)/get-data && make clean-all
	cd $(MAKEFILE_PATH)/process-data && make clean-all

get:
	cd $(MAKEFILE_PATH)/get-data && make run

process:
	cd $(MAKEFILE_PATH)/process-data && make run

run: get process
