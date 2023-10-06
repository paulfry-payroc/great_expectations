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


def prepare_batch_request(gx_data_src, data_asset_name):
    """Prepare a batch request for the given data asset name."""
    batch_request = {
        "datasource_name": gx_data_src,
        "data_connector_name": "default_configured_data_connector_name",
        "data_asset_name": data_asset_name,
        "limit": 1000,
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


def validate_inputs():
    """Validate the presence of required environment variables."""
    gx_data_src = os.getenv("GX_DATA_SRC")
    data_asset_name = os.getenv("SNOWFLAKE_EXAMPLE_TBL")

    if not gx_data_src:
        raise ValueError("GX_DATA_SRC environment variable is not set.")
    if not data_asset_name:
        raise ValueError("SNOWFLAKE_EXAMPLE_TBL environment variable is not set.")

    return gx_data_src, data_asset_name


def main():
    """Main function to execute the data profiling script."""
    try:
        gx_data_src, data_asset_name = validate_inputs()
        batch_request = prepare_batch_request(gx_data_src, data_asset_name)
        expectation_suite_name = prepare_expectation_suite()
        data_assistant_result = run_onboarding_data_assistant(batch_request)
        save_expectation_suite(data_assistant_result, expectation_suite_name)

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
