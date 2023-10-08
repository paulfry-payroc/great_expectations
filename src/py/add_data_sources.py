import os

import great_expectations as gx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Snowflake connection parameters
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")
SNOWFLAKE_EXAMPLE_TBL = os.getenv("SNOWFLAKE_EXAMPLE_TBL")

context = gx.get_context()

# context.sources.add_or_update_snowflake(name="dim_card")

# print(context.datasources["dim_card"])

datasource = context.datasources["gx_datasource_snowflake"]

table_asset = datasource.add_table_asset(name="bkp_change_history", table_name="bkp_change_history")
