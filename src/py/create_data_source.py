import logging
import os

import great_expectations as gx
import yaml
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Set up a specific logger with our desired output level"""
logging.basicConfig(format="%(message)s")
logger = logging.getLogger("application_logger")
logger.setLevel(logging.INFO)

context = gx.get_context()


def create_connection_string():
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


def load_config_from_yaml():
    # Open and read YAML data from a file
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


def main():
    """Main function to execute the script."""
    try:
        input_tables, other_params = load_config_from_yaml()
        gx_data_src_name = other_params["gx_data_src_name"]
        my_connection_string = create_connection_string()
        datasource = context.sources.add_snowflake(
            name=gx_data_src_name,
            connection_string=my_connection_string,
        )

        # add input tables to data source
        for input_table in input_tables:
            logger.info(f"gx_data_src_name = {gx_data_src_name}")
            logger.info(f"table = {input_table}")

            datasource.add_table_asset(name=input_table, table_name=input_table)

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
