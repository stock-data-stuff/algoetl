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

# Some script commands
START=$(shell date --date="10 days ago" +"%Y-%m-%d")
END=$(shell date --date="1 days ago" +"%Y-%m-%d")

all: clean lint run

clean:
	$(info Removing any fetched files)
	$(shell rm -f $(MAKEFILE_PATH)/tmp/*.csv)

clean-all: clean
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

run: clean
	$(info Running the script without any setup...)
	source $(VENV_DIR)/bin/activate && python3 pyalgofetcher.py -s $(START) -e $(END)

pylint: deps
	$(info Running pylint. This is generally has false positives)
	source $(VENV_DIR)/bin/activate && python -m pip install pylint && pylint --rcfile=./.pylintrc ./*.py

pyflakes: deps
	$(info Running pyflakes. This is faster than pylint)
	source $(VENV_DIR)/bin/activate && python -m pip install pyflakes && pyflakes ./*.py

lint: pyflakes pylint
	$(info Running some static code analysis)

