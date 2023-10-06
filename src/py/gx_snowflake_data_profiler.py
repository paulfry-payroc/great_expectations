import logging
import os

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from great_expectations.dataset.pandas_dataset import PandasDataset
from great_expectations.profile.basic_dataset_profiler import BasicDatasetProfiler
from great_expectations.render.renderer import ProfilingResultsPageRenderer
from great_expectations.render.view import DefaultJinjaPageView

# Load environment variables from .env file
load_dotenv()

# Set up a specific logger with our desired output level"""
logging.basicConfig(format="%(message)s")
logger = logging.getLogger("application_logger")
logger.setLevel(logging.INFO)

# Constants
DATA_DOCS_DIR = "gx/uncommitted/data_docs/local_site/"
HTML_FILE_PATH = os.path.join(DATA_DOCS_DIR, "profiling_results.html")


def remove_relative_paths_from_html():
    """Removes occurrences of the string '../../../../' from the profiling_results.html file."""
    # Read the content of the HTML file
    with open(HTML_FILE_PATH) as file:
        content = file.read()

    # Replace the string "../../../../" with an empty string
    modified_content = content.replace("../../../../", "")

    # Write the modified content back to the HTML file
    with open(HTML_FILE_PATH, "w") as file:
        file.write(modified_content)


def create_directory(directory):
    """Create a directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.debug(f"Directory created: {directory}")
    else:
        logger.debug(f"Directory already exists: {directory}")


def generate_data_profiling_html(pandas_dataset):
    # Using BasicDatasetProfiler as a profiler
    profiling_result_document_content = ProfilingResultsPageRenderer().render(
        pandas_dataset.profile(BasicDatasetProfiler)
    )

    # Generate the HTML
    profiling_result_HTML = DefaultJinjaPageView().render(profiling_result_document_content)

    # create the directory below if it doesn't exist
    create_directory(DATA_DOCS_DIR)

    # Write the raw HTML content to files
    with open(f"{DATA_DOCS_DIR}/profiling_results.html", "w") as profiling_results_file:
        profiling_results_file.write(profiling_result_HTML)

    return


def snowflake_query(conn, input_tbl, row_count_limit):
    sql_query = f"SELECT * FROM {input_tbl} LIMIT {row_count_limit};"
    snowflake_cursor = conn.cursor()
    snowflake_cursor.execute(sql_query)
    result = snowflake_cursor.fetchall()
    snowflake_cursor.close()
    conn.close()

    column_names = [desc[0] for desc in snowflake_cursor.description]
    df = pd.DataFrame(result, columns=column_names)

    pandas_dataset = PandasDataset(df)

    return pandas_dataset


def setup_snowflake_connection(snowflake_env_vars):
    snowflake_params = {
        "account": snowflake_env_vars["SNOWFLAKE_ACCOUNT"],
        "user": snowflake_env_vars["SNOWFLAKE_USER"],
        "password": snowflake_env_vars["SNOWFLAKE_PASSWORD"],
        "warehouse": snowflake_env_vars["SNOWFLAKE_WAREHOUSE"],
        "database": snowflake_env_vars["SNOWFLAKE_DATABASE"],
        "schema": snowflake_env_vars["SNOWFLAKE_SCHEMA"],
    }

    conn = snowflake.connector.connect(
        account=snowflake_params["account"],
        user=snowflake_params["user"],
        password=snowflake_params["password"],
        warehouse=snowflake_params["warehouse"],
        database=snowflake_params["database"],
        schema=snowflake_params["schema"],
    )

    return conn


def validate_inputs():
    """Validate the presence of required environment variables."""

    snowflake_env_vars = {}

    env_vars_to_validate = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_ROLE",
        "INPUT_TABLE",
        "ROW_COUNT_LIMIT",
    ]

    for env_var in env_vars_to_validate:
        value = os.getenv(env_var)
        if not value:
            raise ValueError(f"{env_var} environment variable is not set.")
        else:
            snowflake_env_vars[env_var] = value

    return snowflake_env_vars


def main():
    try:
        snowflake_env_vars = validate_inputs()
        conn = setup_snowflake_connection(snowflake_env_vars)
        pandas_dataset = snowflake_query(conn, snowflake_env_vars["INPUT_TABLE"], snowflake_env_vars["ROW_COUNT_LIMIT"])
        generate_data_profiling_html(pandas_dataset)
        remove_relative_paths_from_html()
    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
