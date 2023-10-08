import logging
import re
import warnings
from datetime import datetime

import great_expectations as gx
import yaml
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

    print(batch_request)  # TODO - remove

    try:
        data_assistant_result = context.assistants.onboarding.run(batch_request=batch_request)
        logging.info("Data assistant run successful.")
        return data_assistant_result
    except Exception as e:
        logging.error(f"Error running data assistant: {e}")
        raise


def prepare_expectation_suite(input_table):
    """Prepare and create a new expectation suite with the current date as the name."""
    current_date_str = datetime.now().strftime("%Y%m%d")
    expectation_suite_name = f"{current_date_str}_expectations_{input_table}"

    try:
        context.create_expectation_suite(expectation_suite_name, overwrite_existing=True)
        logging.info(f"Expectation suite '{expectation_suite_name}' created successfully.")
    except Exception as e:
        logging.error(f"Error creating expectation suite: {e}")
        raise
    return expectation_suite_name


def prepare_batch_request(input_table, gx_data_src_name, row_count_limit):
    """Prepare a batch request for the given data asset name."""
    # Retrieve data asset
    my_asset = context.get_datasource(gx_data_src_name).get_asset(input_table)

    """An options dictionary can be used to limit the Batches returned by a Batch Request.
    # Omitting the options dictionary will result in all available Batches being returned."""
    # print(my_asset.batch_request_options)

    # build batch request
    batch_request = my_asset.build_batch_request()

    batches = my_asset.get_batch_list_from_batch_request(batch_request)

    for batch in batches:
        print(batch.batch_spec)

    return batch_request


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
        row_count_limit = other_params["row_count_limit"]

        logger.debug(f"input tables = {input_tables}")
        logger.debug(f"gx_data_src_name = {gx_data_src_name}")
        logger.debug(f"row_count_limit = {row_count_limit}")

        for input_table in input_tables:
            logger.info(f"gx_data_src_name = {gx_data_src_name}")
            logger.info(f"table = {input_table}")
            batch_request = prepare_batch_request(input_table, gx_data_src_name, row_count_limit)
            expectation_suite_name = prepare_expectation_suite(input_table)
            data_assistant_result = run_onboarding_data_assistant(batch_request)
            save_expectation_suite(data_assistant_result, expectation_suite_name)
            checkpoint_result = create_and_run_checkpoint(batch_request, expectation_suite_name)
        modify_html_file("gx/uncommitted/data_docs/local_site/index.html")
        open_dx_data_docs(checkpoint_result)

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
