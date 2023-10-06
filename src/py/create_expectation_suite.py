import logging
import os
import warnings
from datetime import datetime

import great_expectations as gx
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Set up a specific logger with our desired output level"""
logging.basicConfig(format="%(message)s")
logger = logging.getLogger("application_logger")
logger.setLevel(logging.INFO)

# Suppress DeprecationWarning for create_expectation_suite
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Create a GX context
context = gx.get_context()


def prepare_batch_request(env_vars):
    """Prepare a batch request for the given data asset name."""
    batch_request = {
        "datasource_name": env_vars["GX_DATA_SRC"],
        "data_connector_name": "default_configured_data_connector_name",
        "data_asset_name": env_vars["INPUT_TABLE"],
        "limit": int(env_vars["ROW_COUNT_LIMIT"]),
    }
    return batch_request


def prepare_expectation_suite():
    """Prepare and create a new expectation suite with the current date as the name."""
    current_date_str = datetime.now().strftime("%Y_%m_%d")
    expectation_suite_name = f"data_profiling_suite_{current_date_str}"

    try:
        context.create_expectation_suite(expectation_suite_name, overwrite_existing=True)
        logging.info(f"Expectation suite '{expectation_suite_name}' created successfully.")
    except Exception as e:
        logging.error(f"Error creating expectation suite: {e}")
        raise
    return expectation_suite_name


def run_onboarding_data_assistant(batch_request, exclude_column_names=[]):
    """Run onboarding data assistant with the provided batch request and exclude column names."""
    try:
        data_assistant_result = context.assistants.onboarding.run(
            batch_request=batch_request,
            exclude_column_names=exclude_column_names,
        )
        logging.info("Data assistant run successful.")
        return data_assistant_result
    except Exception as e:
        logging.error(f"Error running data assistant: {e}")
        raise


def save_expectation_suite(data_assistant_result, expectation_suite_name):
    """Save the expectation suite obtained from the data assistant."""
    try:
        expectation_suite = data_assistant_result.get_expectation_suite(expectation_suite_name=expectation_suite_name)
        context.add_or_update_expectation_suite(expectation_suite=expectation_suite)
        logging.info(f"Expectation suite '{expectation_suite_name}' saved successfully.")
    except Exception as e:
        logging.error(f"Error saving expectation suite: {e}")
        raise


def wip(batch_request, expectation_suite_name):
    checkpoint = context.add_or_update_checkpoint(
        name="my_checkpoint",
        validations=[
            {
                "batch_request": batch_request,
                "expectation_suite_name": expectation_suite_name,
            },
        ],
    )
    checkpoint.run()
    context.build_data_docs()


def validate_inputs():
    """Validate the presence of required environment variables and return them as a dictionary."""

    # List of environment variables to validate
    env_vars_to_validate = ["GX_DATA_SRC", "INPUT_TABLE", "ROW_COUNT_LIMIT"]

    env_vars = {}
    for env_var in env_vars_to_validate:
        value = os.getenv(env_var)
        if not value:
            raise ValueError(f"{env_var} environment variable is not set.")
        else:
            env_vars[env_var] = value
            logger.debug(f"env_var '{env_var}' = {value}")
    return env_vars


def main():
    """Main function to execute the script."""
    try:
        env_vars = validate_inputs()
        batch_request = prepare_batch_request(env_vars)
        expectation_suite_name = prepare_expectation_suite()
        data_assistant_result = run_onboarding_data_assistant(batch_request)
        save_expectation_suite(data_assistant_result, expectation_suite_name)
        wip(batch_request, expectation_suite_name)

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
