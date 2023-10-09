import logging
import os

import yaml


def get_logger():
    """Set up a specific logger with desired output level"""
    logging.basicConfig(format="%(message)s")
    logger = logging.getLogger("application_logger")
    logger.setLevel(logging.INFO)

    return logger


def load_config_from_yaml():
    # Open and read YAML data from a file

    logger = get_logger()

    with open("config.yaml") as file:
        # Load YAML data into a Python dictionary
        data = yaml.safe_load(file)

    input_tables = data.get("input_tables")
    other_params = data.get("other_params", {})

    # Validate if "input_tables" key is present, is a list, and is not empty
    if (
        input_tables is None
        or not isinstance(input_tables, list)
        or not input_tables
        or all(not item for item in input_tables)
    ):
        raise ValueError("Invalid or empty 'input_tables' in the YAML file.")

    # Validate if the required keys in other_params are present
    required_other_params_keys = ["gx_data_src_name", "row_count_limit"]
    for key in required_other_params_keys:
        if key is None or key not in other_params or not other_params[key]:
            raise ValueError(f"Invalid or missing key '{key}' in other_params.")

    input_tables_lowercase = [table.lower() for table in input_tables]

    logger.debug(input_tables_lowercase)
    logger.debug(other_params)

    return input_tables_lowercase, other_params


def create_snowflake_connection_string():
    # Snowflake connection parameters
    SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
    SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
    SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
    SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
    SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
    SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
    SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")

    my_connection_string = f"snowflake://{SNOWFLAKE_USER}:{SNOWFLAKE_PASSWORD}@{SNOWFLAKE_ACCOUNT}/{SNOWFLAKE_DATABASE}/{SNOWFLAKE_SCHEMA}?warehouse={SNOWFLAKE_WAREHOUSE}&role={SNOWFLAKE_ROLE}"  # noqa

    return my_connection_string
