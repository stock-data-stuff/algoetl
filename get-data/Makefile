.PHONY=all clean clean-all venv python3 deps run lint pylint pyflakes

# Force make to run targets sequentially
.NOTPARALLEL:

# Directory containing this makefile. Includes trailing /
MAKEFILE_PATH=$(dir $(realpath $(firstword $(MAKEFILE_LIST))))

# Path to the virtual environment
VENV_DIR=$(MAKEFILE_PATH).env

# Set default shell as bash
# This is necessary because we use "source" below
SHELL:=/bin/bash

# Specify which python version to use to make a virtual environment
#VENV_PYTHON=/usr/bin/python3.9
VENV_PYTHON=python3

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

all: lint run

clean:
    $(info Clean [noop])

clean-all:
	$(info Removing venv dir)
	$(shell rm -rf $(VENV_DIR))

venv:
	$(info Installing/Updating venv using $(VENV_PYTHON))
	test -d $(VENV_DIR) || $(VENV_PYTHON) -m venv $(VENV_DIR)

python3: venv
	$(info Installing/Updating Python requirements)
	source $(VENV_DIR)/bin/activate && pip3 -q install -r $(MAKEFILE_PATH)requirements.txt

deps: python3
	$(info Installing dependencies)

pylint: deps
	$(info Running pylint. This is generally has false positives)
	source $(VENV_DIR)/bin/activate && python -m pip install pylint && pylint --rcfile=./.pylintrc ./*.py

pyflakes: deps
	$(info Running pyflakes. This is faster than pylint)
	source $(VENV_DIR)/bin/activate && python -m pip install pyflakes && pyflakes ./*.py

lint: pyflakes pylint
	$(info Running some static code analysis)

run-script:
	$(info Running the script for START=$(START) and END=$(END))
	#source $(VENV_DIR)/bin/activate && python3 pyalgofetcher.py -s $(START) -e $(END)

run: deps lint run-script
