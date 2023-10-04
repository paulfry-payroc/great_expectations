# flake8: noqa
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

my_connection_string = f"snowflake://{SNOWFLAKE_USER}:{SNOWFLAKE_PASSWORD}@{SNOWFLAKE_ACCOUNT}/{SNOWFLAKE_DATABASE}/{SNOWFLAKE_SCHEMA}?warehouse={SNOWFLAKE_WAREHOUSE}&role={SNOWFLAKE_ROLE}"

datasource_name = "v2_my_snowflake_datasource"

datasource = context.sources.add_snowflake(
    name=datasource_name,
    connection_string=my_connection_string,  # Or alternatively, individual connection args
)

asset_name = "my_asset"
asset_table_name = SNOWFLAKE_EXAMPLE_TBL

table_asset = datasource.add_table_asset(name=asset_name, table_name=asset_table_name)

asset_name = "my_query_asset"
query = "SELECT * FROM BKP_CHANGE_HISTORY"

query_asset = datasource.add_query_asset(name=asset_name, query=query)
