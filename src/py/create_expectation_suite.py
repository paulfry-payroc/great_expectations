import os
from datetime import datetime

import great_expectations as gx
import great_expectations.jupyter_ux
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

context = gx.get_context()

SNOWFLAKE_EXAMPLE_TBL = os.getenv("SNOWFLAKE_EXAMPLE_TBL")
# TODO - read in as input
GX_DATA_SRC = "gx_datasource_snowflake"

current_date_str = datetime.now().strftime("%Y_%m_%d")

expectation_suite_name = f"data_profiling_suite_{current_date_str}"

batch_request = {
    "datasource_name": GX_DATA_SRC,
    "data_connector_name": "default_configured_data_connector_name",
    "data_asset_name": SNOWFLAKE_EXAMPLE_TBL,
    "limit": 1000,
}

###

expectation_suite = context.add_or_update_expectation_suite(expectation_suite_name=expectation_suite_name)

exclude_column_names = []

data_assistant_result = context.assistants.onboarding.run(
    batch_request=batch_request,
    exclude_column_names=exclude_column_names,
)

expectation_suite = data_assistant_result.get_expectation_suite(expectation_suite_name=expectation_suite_name)

context.add_or_update_expectation_suite(expectation_suite=expectation_suite)
