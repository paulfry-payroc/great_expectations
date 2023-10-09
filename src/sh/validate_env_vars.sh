#!/bin/bash

#=======================================================================
# Variables
#=======================================================================

# setup colour formatting
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
COLOUR_OFF='\033[0m' # Text Reset

# Load environment variables from .env file
source .env

env_vars_to_validate=("SNOWFLAKE_ACCOUNT" "SNOWFLAKE_USER" "SNOWFLAKE_PASSWORD" "SNOWFLAKE_DATABASE" "SNOWFLAKE_SCHEMA" "SNOWFLAKE_WAREHOUSE" "SNOWFLAKE_ROLE")

#=======================================================================
# Main script logic
#=======================================================================
# Validate .env file
echo "Validating .env file."

for var in "${env_vars_to_validate[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not defined in .env file"
        exit 1
    fi
done

# Validate input_tables, row_count_limit, and gx_data_src_name in config.yaml
echo "Validating input_tables, row_count_limit, and gx_data_src_name in config.yaml..."
input_tables=$(grep -E '^input_tables:' config.yaml | sed 's/input_tables:\s*//')
row_count_limit=$(grep -E '^row_count_limit:' config.yaml | sed 's/row_count_limit:\s*//')
gx_data_src_name=$(grep -E '^gx_data_src_name:' config.yaml | sed 's/gx_data_src_name:\s*//')

if [ -z "$input_tables" ]; then
    echo "Error: input_tables is not defined in config.yaml or the list is empty"
    exit 1
fi

if [ -z "$row_count_limit" ] || [ -z "$gx_data_src_name" ]; then
    echo "Error: row_count_limit and gx_data_src_name must be defined in config.yaml"
    exit 1
fi

echo "Validation successful."
