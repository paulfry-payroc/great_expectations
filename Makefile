SHELL = /bin/sh

#================================================================
# Usage
#================================================================
# make deps		# just install the dependencies
# make install		# perform the end-to-end install
# make create_gx_profiler_and_expectation_suite		# Create the GX data profiles & expectation suite
# make clean		# clean up/restore the repo back to its' original form
#=======================================================================
# Variables
#=======================================================================
.EXPORT_ALL_VARIABLES:

# load variables from separate file
include config.mk

VENV_ACTIVATE := . ./.venv/bin/activate

#=======================================================================
# Targets
#=======================================================================
all: clean deps install create_gx_profiler_and_expectation_suite update_gx_data_docs

deps:
	@echo && echo "${YELLOW}Called makefile target 'deps'. Create virtualenv with required Python libs.${COLOUR_OFF}" && echo
	@echo "${PURPLE}Create a virtualenv (.venv) with the required Python libraries installed - see requirements.txt.${COLOUR_OFF}"
	@python3 --version >/dev/null 2>&1 || (echo "Python 3 is required but not found"; exit 1)
	@python3 -m venv .venv && chmod +x ./.venv/bin/activate
	@python3 -m venv --help >/dev/null 2>&1 || (echo "Python venv module not found"; exit 1)
	@test -f requirements.txt || (echo && echo "${RED}Error: requirements.txt file not found.${COLOUR_OFF}" && echo; exit 1)
	@${VENV_ACTIVATE} && pip install -r requirements.txt -q

abc: validate_env_vars
	@#echo "test"

install: validate_env_vars
	@echo && echo "${YELLOW}Called makefile target 'install'. Set up GX (Great Expectations) project.${COLOUR_OFF}" && echo
	@echo "${PURPLE}Step 1: Initialise GX project.${COLOUR_OFF}"
	@${VENV_ACTIVATE} && echo "Y" | great_expectations init --no-usage-stats > /dev/null 2>&1
	@echo "${PURPLE}Step 2: Add Snowflake tables to GX project.${COLOUR_OFF}"
	@${VENV_ACTIVATE} && python3 src/py/create_gx_snowflake_table_loader.py

create_gx_profiler_and_expectation_suite:
	@echo && echo "${YELLOW}Called makefile target 'create_gx_profiler_and_expectation_suite'.${COLOUR_OFF}" && echo
	@${VENV_ACTIVATE} && python3 src/py/create_gx_data_profiler.py
	@${VENV_ACTIVATE} && python3 src/py/create_gx_expectation_suite.py

update_gx_data_docs:
	@echo && echo "${YELLOW}Called makefile target 'update_gx_data_docs'.${COLOUR_OFF}" && echo
	@${VENV_ACTIVATE} && python3 src/py/update_gx_data_docs.py

validate_env_vars:
	@echo && echo "${YELLOW}Called makefile target 'validate_env_vars'. Verify the contents of required env vars.${COLOUR_OFF}" && echo
	@./src/sh/validate_env_vars.sh config.yaml .env

clean:
	@echo && echo "${YELLOW}Called makefile target 'clean'. Restoring the repository to its initial state.${COLOUR_OFF}" && echo
	@echo "${PURPLE}* Delete the virtualenv directory${COLOUR_OFF}" && rm -rf .venv
	@echo "${PURPLE}* Delete the generated GX directory${COLOUR_OFF}" && rm -rf gx

clean_gx:
	@echo "Cleaning GX (Great Expectations) directories."
	@rm -rf gx/uncommitted/data_docs/local_site/*
	@rm -rf gx/uncommitted/validations/*
	@rm -rf gx/checkpoints/*
	@rm -rf gx/expectations/*

# Phony targets
.PHONY: all deps install test clean
# .PHONY tells Make that these targets don't represent files
# This prevents conflicts with any files named "all" or "clean"
