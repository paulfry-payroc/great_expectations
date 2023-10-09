SHELL = /bin/sh

#================================================================
# Usage
#================================================================
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
all: clean deps install test_connection

deps:
	@echo && echo "${PURPLE}Create a virtualenv (.venv) with the required Python libraries installed - see requirements.txt.${COLOUR_OFF}"
	@python3 -m venv .venv && chmod +x ./.venv/bin/activate
	@${VENV_ACTIVATE} && pip install -r requirements.txt -q

install:
	@echo && echo "${YELLOW}Called makefile target 'install'. Set up GX (Great Expectations) project.${COLOUR_OFF}" && echo
	@echo "${PURPLE}Step 1: Initialise GX project.${COLOUR_OFF}"
	@${VENV_ACTIVATE} && echo "Y" | great_expectations init --no-usage-stats > /dev/null 2>&1
	@echo "${PURPLE}Step 2: Add Snowflake tables to GX project.${COLOUR_OFF}"
	@${VENV_ACTIVATE} && python3 src/py/add_sf_tbls_to_gx_project.py && echo

a:
	@${VENV_ACTIVATE} && python3 src/py/v1_data_profiler.py

b:
	@${VENV_ACTIVATE} && python3 src/py/create_expectation_suite.py


create_data_profile:
	# TODO - WIP
	@${VENV_ACTIVATE} && python3 src/py/v1_data_profiler.py
	@${VENV_ACTIVATE} && python3 src/py/create_expectation_suite.py

clean_gx:
	# TODO - remove/tidy this up
	@rm -rf gx/uncommitted/validations/*
	@rm -rf gx/checkpoints/*
	@rm -rf gx/expectations/*
	@rm -rf gx/uncommitted/data_docs/local_site/*

clean:
	@echo && echo "${YELLOW}Called makefile target 'clean'. Restore the repo to it's initial state - i.e., remove all generated files.${COLOUR_OFF}" && echo
	@echo "${PURPLE}* Delete the virtualenv directory & delete the generated .env file${COLOUR_OFF}"
	@rm -rf .venv
	@echo "${PURPLE}* Delete the generated GX (greate expectations) directory${COLOUR_OFF}"
	@rm -rf gx

# Phony targets
.PHONY: all deps install test clean
# .PHONY tells Make that these targets don't represent files
# This prevents conflicts with any files named "all" or "clean"
