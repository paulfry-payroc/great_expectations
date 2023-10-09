#!/usr/bin/env python3
"""
Description: Executes a Snowflake command using the snowflake-connector-python library.
Date: 2023-08-30
"""

__author__ = "Paul Fry"
__version__ = "1.0"

import os
import sys
import argparse
import logging
import json
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(format="%(message)s")
logger = logging.getLogger("application_logger")
logger.setLevel(logging.INFO)

# Constants
REQUIRED_ENV_VARS = [
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
    "SNOWFLAKE_SCHEMA",
]


def execute_snowflake_command(cursor, sql_command, query_result_str=""):
    """Execute Snowflake command(s)"""
    try:
        # Execute the SQL command
        cursor.execute(sql_command)

        # Fetch all results
        query_results = cursor.fetchall()

        # If there are no results, log a message and return an empty string and the cursor
        if not query_results:
            logger.info("No results returned.")
            return "", cursor

        # Convert each row to a string and join them with commas
        query_result_str = "\n".join(", ".join(map(str, row)) for row in query_results)
        logger.info(query_result_str)

        return query_result_str, cursor

    except Exception as e:
        logging.exception("An error occurred while executing Snowflake command: %s", e)
        sys.exit(1)


def execute_sql_from_file(conn, sql_file, input_args=None):
    """Execute SQL statements from an input SQL file."""

    try:
        with open(sql_file) as file:
            sql_commands = file.read()

        # Split the SQL commands based on the delimiter (e.g., semicolon)
        sql_commands_list = sql_commands.split(";")

        with conn.cursor() as cursor:
            for sql_command in sql_commands_list:
                sql_command = sql_command.strip()  # Remove leading/trailing whitespace

                # Skip empty statements and comments
                if sql_command and not sql_command.startswith("--"):
                    if input_args:
                        sql_command = sql_command.format(**input_args)  # Replace placeholders with input arguments
                    query_result_str, cursor = execute_snowflake_command(cursor, sql_command)

    except Exception as e:
        logging.exception("An error occurred while executing SQL from file: %s", e)
        sys.exit(1)


def create_snowflake_connection():
    """Create a Snowflake connection instance and cursor."""

    # Store the Snowflake connection parameters from environment variables
    conn_params = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
    }

    try:
        # Connect to Snowflake
        conn = snowflake.connector.connect(**conn_params)

        # Create a cursor
        cursor = conn.cursor()

        return conn, cursor

    except (snowflake.connector.errors.ProgrammingError, snowflake.connector.errors.DatabaseError) as e:
        if e.errno == 251005:
            message = f"Invalid username/password. Message: '{e.msg}'."
        elif e.errno == 250001:
            message = f"Invalid Snowflake account name provided. Message: '{e.msg}'."
        else:
            message = f"Error {e.errno} ({e.sqlstate}): ({e.sfqid})"
        logger.error(f"\nERROR: {message}\n")
        sys.exit(1)


def validate_env_vars(required_env_vars):
    """Verify whether the required environment variables exist."""

    missing_env_vars = [var for var in required_env_vars if os.getenv(var) is None]
    if missing_env_vars:
        logger.error("\nError: The following environment variables are missing:\n")
        for var in missing_env_vars:
            logger.error(var)
        exit(1)


def validate_input_args(sql_query=None, sql_file=None):
    """Validate that an input arg has been provided"""

    if not sql_query and not sql_file:
        logger.error("Error: You must provide either --sql-command or --sql-file.")
        sys.exit(1)


def main(sql_query=None, sql_file=None, args_json=None, cursor=None):
    """Main entry point of the script."""

    try:
        # Validate that an input arg has been provided
        validate_input_args(sql_query, sql_file)

        # Verify whether the required environment variables exist
        validate_env_vars(REQUIRED_ENV_VARS)

        # Connect to Snowflake DB
        conn, cursor = create_snowflake_connection()

        # If a SQL file has been passed in, we need to split the SQL commands by semicolon
        if sql_file:
            input_args = {}  # Initialize an empty dictionary for input arguments
            if args_json:
                input_args = json.loads(args_json)
            execute_sql_from_file(cursor, sql_file, input_args)
        else:
            # Execute the Snowflake command
            query_result_str, cursor = execute_snowflake_command(cursor, sql_query)

        # Close the cursor and connection when done
        cursor.close()
        conn.close()

    except Exception as e:
        logger.exception("An unexpected error occurred: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    """This is executed when run from the command line"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Execute a Snowflake command.")
    parser.add_argument("--sql-query", help="Snowflake SQL command to execute")
    parser.add_argument("--sql-file", help="Path to a .sql file containing the SQL command")
    parser.add_argument("--args-json", help="JSON string containing input arguments for SQL placeholders")
    args = parser.parse_args()

    # Call the modified main function with command line arguments
    main(args.sql_query, args.sql_file, args.args_json)
