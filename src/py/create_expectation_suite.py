import logging
import os
import re
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


def open_dx_data_docs(checkpoint_result):
    """Open the data documentation for the first validation result in the given checkpoint result."""
    validation_result_identifier = checkpoint_result.list_validation_result_identifiers()[0]
    context.open_data_docs(resource_identifier=validation_result_identifier)


def modify_html_file(file_path):
    """Modifies the specified HTML file content, replacing the specified text."""

    # Read the content of the HTML file
    with open(file_path) as file:
        content = file.read()

    # Define the pattern to be found using a regular expression
    old_text_pattern = r'<li class="nav-item">\s*<a\s*class="nav-link"\s*id="Expectation-Suites-tab"\s*data-toggle="tab"\s*href="#Expectation-Suites"\s*role="tab"\s*aria-selected="false"\s*aria-controls="Expectation-Suites">\s*Expectation Suites\s*</a>\s*</li>'  # noqa

    # Specify the text to be replaced and its replacement
    # old_text = (
    #     '<li class="nav-item">\n'
    #     '    <a class="nav-link" id="Expectation-Suites-tab" data-toggle="tab" href="#Expectation-Suites"\n'
    #     '      role="tab" aria-selected="false" aria-controls="Expectation-Suites">\n'
    #     "      Expectation Suites\n"
    #     "    </a>\n"
    #     "  </li>"
    # )

    # Define the replacement text
    new_text = (
        '<li class="nav-item">\n'
        '    <a class="nav-link" id="Expectation-Suites-tab" href="profiling_results.html"\n'
        '      aria-selected="false" aria-controls="Expectation-Suites">\n'
        "      Profiling Results\n"
        "    </a>\n"
        "  </li>\n"
        "\n"
        '  <li class="nav-item">\n'
        '    <a class="nav-link" id="Expectation-Suites-tab" data-toggle="tab" href="#Expectation-Suites"\n'
        '      role="tab" aria-selected="false" aria-controls="Expectation-Suites">\n'
        "      Expectation Suites\n"
        "    </a>\n"
        "  </li>"
    )

    # Use regular expressions to replace the old text with the new text in the content
    modified_content = re.sub(old_text_pattern, new_text, content)

    # Write the modified content back to the file
    with open(file_path, "w") as file:
        file.write(modified_content)


def create_and_run_checkpoint(batch_request, expectation_suite_name):
    """Create a checkpoint, run validations, and build data documentation."""
    checkpoint = context.add_or_update_checkpoint(
        name="my_checkpoint",
        validations=[
            {
                "batch_request": batch_request,
                "expectation_suite_name": expectation_suite_name,
            },
        ],
    )
    checkpoint_result = checkpoint.run()
    context.build_data_docs()

    return checkpoint_result


def save_expectation_suite(data_assistant_result, expectation_suite_name):
    """Save the expectation suite obtained from the data assistant."""
    try:
        expectation_suite = data_assistant_result.get_expectation_suite(expectation_suite_name=expectation_suite_name)
        context.add_or_update_expectation_suite(expectation_suite=expectation_suite)
        logging.info(f"Expectation suite '{expectation_suite_name}' saved successfully.")
    except Exception as e:
        logging.error(f"Error saving expectation suite: {e}")
        raise


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


def prepare_expectation_suite():
    """Prepare and create a new expectation suite with the current date as the name."""
    current_date_str = datetime.now().strftime("%Y%m%d")
    expectation_suite_name = f"{current_date_str}_expectation_suite"

    try:
        context.create_expectation_suite(expectation_suite_name, overwrite_existing=True)
        logging.info(f"Expectation suite '{expectation_suite_name}' created successfully.")
    except Exception as e:
        logging.error(f"Error creating expectation suite: {e}")
        raise
    return expectation_suite_name


def prepare_batch_request(env_vars):
    """Prepare a batch request for the given data asset name."""
    batch_request = {
        "datasource_name": env_vars["GX_DATA_SRC"],
        "data_connector_name": "default_configured_data_connector_name",
        "data_asset_name": env_vars["INPUT_TABLE"],
        "limit": int(env_vars["ROW_COUNT_LIMIT"]),
    }
    return batch_request


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
        checkpoint_result = create_and_run_checkpoint(batch_request, expectation_suite_name)
        modify_html_file("gx/uncommitted/data_docs/local_site/index.html")
        open_dx_data_docs(checkpoint_result)

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
