SHELL = /bin/sh

#================================================================
# Usage
#================================================================
# make installations	# install the package for the first time, managing dependencies & performing a housekeeping cleanup too
# make deps		# just install the dependencies
# make install		# perform the end-to-end install
# make clean		# perform a housekeeping cleanup

#=======================================================================
# Variables
#=======================================================================
.EXPORT_ALL_VARIABLES:

# load variables from separate file
include config.mk

# Load environment variables from .env file
include .env

VENV_ACTIVATE := . ./.venv/bin/activate
GX_PROJECT_DIR := gx
GX_DATA_SRC := gx_datasource_snowflake

#=======================================================================
# Targets
#=======================================================================
all: clean deps install test

deps:
	@echo && echo "${YELLOW}Called makefile target: 'deps'. Generate VENV with required pip packages.${COLOUR_OFF}" && echo
	@echo "${PURPLE}Step 1: Create a virtualenv (.venv) with the required Python libraries - see requirements.txt.${COLOUR_OFF}"
	@python3 -m venv .venv && chmod +x ./.venv/bin/activate
	@${VENV_ACTIVATE} && pip install -r requirements.txt -q

install:
	@echo && echo "${YELLOW}Called makefile target: 'install'. Run the setup and install targets.${COLOUR_OFF}" && echo
	@echo "${PURPLE}Step 1: Create Great Expectations Project directory.${COLOUR_OFF}"
	@${VENV_ACTIVATE} && echo "Y" | great_expectations init --no-usage-stats > /dev/null 2>&1
	@echo "${PURPLE}Step 2: Render GX jinja template files.${COLOUR_OFF}"
	@j2 src/templates/jinja_templates/great_expectations.yml.j2 -o ${GX_PROJECT_DIR}/great_expectations.yml

test:
	@echo && echo "${YELLOW}Called makefile target 'test'. Test the GX data source connection.${COLOUR_OFF}" && echo
	@${VENV_ACTIVATE} && python3 src/py/test_snowflake_connection.py

create_data_profile:
	@${VENV_ACTIVATE} && python3 src/py/gx_snowflake_data_profiler.py
	@${VENV_ACTIVATE} && python3 src/py/create_expectation_suite.py

clean:
	@echo && echo "${YELLOW}Called makefile target 'clean'. Purpose: restore the repo to it's initial state (i.e., remove all generated/created files).${COLOUR_OFF}" && echo
	@echo "${PURPLE}* Delete the virtualenv directory & delete the generated .env file${COLOUR_OFF}"
	@rm -rf .venv
	@echo "${PURPLE}* Delete the generated GX (greate expectations) directory${COLOUR_OFF}"
	@rm -rf gx

clean_gx:
	@rm -rf gx/uncommitted/validations/*
	@rm -rf gx/checkpoints/*
	@rm -rf gx/expectations/*
	@rm -rf gx/uncommitted/data_docs/local_site/*

# Phony targets
.PHONY: all deps install test clean

# .PHONY tells Make that these targets don't represent files
# This prevents conflicts with any files named "all" or "clean"
