import logging
import os

import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class InvalidYAMLFileError(Exception):
    pass


class MissingEnvironmentVariableError(Exception):
    pass


def get_logger(log_level=logging.INFO):
    """Set up a specific logger with desired output level"""

    logging.basicConfig(format="%(message)s")
    logger = logging.getLogger("application_logger")
    logger.setLevel(log_level)
    return logger


def load_config_from_yaml(file_path="config.yaml"):
    """Load and validate configuration data from a YAML file."""

    try:
        logger = get_logger()

        with open(file_path) as file:
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

        logger.debug(input_tables)
        logger.debug(other_params)

    except FileNotFoundError:
        raise InvalidYAMLFileError(f"YAML file '{file_path}' not found.")
    except yaml.YAMLError as e:
        raise InvalidYAMLFileError(f"Error loading YAML: {e}")

    return input_tables, other_params


def validate_environment_variables():
    """Validates required Snowflake connection environment variables."""

    REQUIRED_ENV_VARS = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_ROLE",
    ]
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            raise MissingEnvironmentVariableError(f"Environment variable '{var}' is not set.")


def create_snowflake_connection_string():
    """Creates and returns a Snowflake connection string based on environment variables."""

    # validate that the env vars exist
    validate_environment_variables()

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
