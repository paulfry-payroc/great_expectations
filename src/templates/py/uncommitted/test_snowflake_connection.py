import os

import great_expectations as gx
from dotenv import load_dotenv
from ruamel import yaml  # noqa

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


datasource_yaml = f"""
name: test_ds_conn
class_name: Datasource
execution_engine:
  class_name: SqlAlchemyExecutionEngine
  credentials:
    host: {SNOWFLAKE_ACCOUNT}
    username: {SNOWFLAKE_USER}
    database: {SNOWFLAKE_DATABASE}
    query:
      schema: {SNOWFLAKE_SCHEMA}
      warehouse: {SNOWFLAKE_WAREHOUSE}
      role: {SNOWFLAKE_ROLE}
    password: {SNOWFLAKE_PASSWORD}
    drivername: snowflake
data_connectors:
  default_runtime_data_connector_name:
    class_name: RuntimeDataConnector
    batch_identifiers:
      - default_identifier_name
  default_inferred_data_connector_name:
    class_name: InferredAssetSqlDataConnector
    include_schema_name: True
    introspection_directives:
      schema_name: {SNOWFLAKE_SCHEMA}
  default_configured_data_connector_name:
    class_name: ConfiguredAssetSqlDataConnector
    assets:
      {SNOWFLAKE_EXAMPLE_TBL}:
        class_name: Asset
        schema_name: {SNOWFLAKE_SCHEMA}
"""
print(datasource_yaml)

# test the connection
context.test_yaml_config(yaml_config=datasource_yaml)

# context.add_datasource(**yaml.load(datasource_yaml))
