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
GX_DATA_SRC := my_datasource

#=======================================================================
# Targets
#=======================================================================
all: deps install test

deps:
	@echo "----------------------------------------------------------------------------------------------------------------------"
	@echo "${YELLOW}Target: 'deps'. Download the relevant pip package dependencies.${COLOUR_OFF}"
	@echo "----------------------------------------------------------------------------------------------------------------------"
	@echo "${PURPLE}Step 1: Create a virtualenv (.venv) with the required Python libraries (see requirements.txt)${COLOUR_OFF}"
	@python3 -m venv .venv && chmod +x ./.venv/bin/activate
	@${VENV_ACTIVATE} && pip install -r requirements.txt -q
	@echo "${PURPLE}Step 2: Generate .env file${COLOUR_OFF}"
	@j2 src/templates/jinja_templates/.env.j2 -o .env

install:
	@echo "${YELLOW}Target: 'install'. Run the setup and install targets.${COLOUR_OFF}"
	@echo "${PURPLE}Step 1: Create Great Expectations Project Dir${COLOUR_OFF}"
	@${VENV_ACTIVATE} && great_expectations init
	@echo "${PURPLE}Step 2: Render GX template files${COLOUR_OFF}"
	@j2 src/templates/jinja_templates/great_expectations.yml.j2 -o ${GX_PROJECT_DIR}/great_expectations.yml
	@echo "${PURPLE}Step 3: Copy python scripts over${COLOUR_OFF}"
	@cp src/templates/py/uncommitted/test_snowflake_connection.py ${GX_PROJECT_DIR}/uncommitted/test_snowflake_connection.py

test:
	@echo "${YELLOW}Target 'test'. Perform any required tests.${COLOUR_OFF}"
	@${VENV_ACTIVATE} && python3 gx/uncommitted/test_snowflake_connection.py

one:
	@${VENV_ACTIVATE} && python3 gx/uncommitted/create_expectation_suite.py

two:
	@${VENV_ACTIVATE} && python3 gx/uncommitted/profile_data.py


clean:
	@echo "${YELLOW}Target 'clean'. Remove any redundant files, e.g. downloads.${COLOUR_OFF}"
	@echo "${PURPLE}Delete the virtualenv directory & delete the generated .env file${COLOUR_OFF}"
	@rm -rf .venv && rm -f .env
	@rm -rf gx

# Phony targets
.PHONY: all deps install test clean

# .PHONY tells Make that these targets don't represent files
# This prevents conflicts with any files named "all" or "clean"
