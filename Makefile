.PHONY=all clean clean-all run get process

# Force make to run targets sequentially
.NOTPARALLEL:

# Directory containing this makefile. Includes trailing /
MAKEFILE_PATH=$(dir $(realpath $(firstword $(MAKEFILE_LIST))))

# Set default shell as bash
SHELL:=/bin/bash

# Set the start and end day.
#
# Normally, these will be given as parameters. e.g.:
#   make START=2022-01-08 END=2022-01-09
#
# But, allow some defaults to be set here.
DEFAULT_START=$(shell date --date="10 days ago" +"%Y-%m-%d")
DEFAULT_END=$(shell date --date="1 day ago" +"%Y-%m-%d")
#
ifndef START
override START = $(DEFAULT_START)
endif
#
ifndef END
override END = $(DEFAULT_END)
endif

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
	cd $(MAKEFILE_PATH)/get-data && make run START=$(START) END=$(END)

process:
	cd $(MAKEFILE_PATH)/process-data && make run

run: get process
