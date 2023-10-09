import logging

import common
import great_expectations as gx

# Set up a specific logger with our desired output level"""
logger = common.get_logger()

context = gx.get_context()


def main():
    """Main function to execute the script."""

    snowflake_conn_string = "snowflake://{SNOWFLAKE_USER}:{SNOWFLAKE_PASSWORD}@{SNOWFLAKE_ACCOUNT}/{SNOWFLAKE_DATABASE}/{SNOWFLAKE_SCHEMA}?warehouse={SNOWFLAKE_WAREHOUSE}&role={SNOWFLAKE_ROLE}"  # noqa

    try:
        input_tables, other_params = common.load_config_from_yaml()
        gx_data_src_name = other_params["gx_data_src_name"]
        row_count_limit = other_params["row_count_limit"]
        datasource = context.sources.add_snowflake(
            name=gx_data_src_name,
            connection_string=snowflake_conn_string,
        )

        # add input tables to data source
        for input_table in input_tables:
            logger.debug(f"gx_data_src_name = {gx_data_src_name}")
            logger.debug(f"table = {input_table}")

            datasource.add_query_asset(name=input_table, query=f"SELECT * FROM {input_table} LIMIT {row_count_limit}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
