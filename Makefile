.PHONY=all clean clean-all venv python3 deps test run

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

# Some script commands
INSTALL_VENV=$(shell test -d $(VENV_DIR) || $(VENV_PYTHON) -m venv $(VENV_DIR))
UPDATE_PIPS=$(shell source $(VENV_DIR)/bin/activate && pip3 -q install -r $(MAKEFILE_PATH)requirements.txt)
START=$(shell date --date="10 days ago" +"%Y-%m-%d")
END=$(shell date --date="1 days ago" +"%Y-%m-%d")
RUN_IMPORT=$(shell source $(VENV_DIR)/bin/activate && python3 pyalgofetcher.py -s $(START) -e $(END))

all: clean test

clean:
	$(info Removing any fetched files)
	$(shell rm -f $(MAKEFILE_PATH)*.csv)

clean-all: clean
	$(info Removing venv dir)
	$(shell rm -rf $(VENV_DIR))

venv:
	$(info Installing/Updating venv using $(VENV_PYTHON))
	$(INSTALL_VENV)

python3: venv
	$(info Installing/Updating Python requirements)
	$(UPDATE_PIPS)

deps: python3
	$(info Installing dependencies)

test: deps
	$(info test the script)
	$(RUN_IMPORT)

run: clean
	$(info Running the script without any setup...)
	$(RUN_IMPORT)

# $(shell) munges the output onto one line
lint: deps
	$(info Running some static code analysis)
	source $(VENV_DIR)/bin/activate && python -m pip install pylint && pylint ./*.py

