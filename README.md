# Bulk Data Profiling using Great Expectations

This repository provides a streamlined way to perform data profiling on a list of input tables using Great Expectations. Follow the instructions below to set up and run the data profiling process.

## Prerequisites

Before you begin, ensure you have the following in place:

`.env` File

- Create a `.env` file by copying the template from `.env_template` and populate the necessary environment variables.

`config.yaml`

- Modify `config.yaml` to list the input tables you want to profile under the key `input_tables`.

## Setup

1. **Create and populate the `.env` file:**

   ```shell
   cp .env_template .env
   # Edit .env and add your environment variables
    ```

2. Configure the input tables in config.yaml:

    ```shell
    input_tables:
    - table_name_1
    - table_name_2
    # Add more input tables as needed
    ```

## Usage

Once you have set up the `.env` file and configured the input tables in `config.yaml`, you can run the data profiling process using the following command:

```shell
make all
```

This command will:

- Create a Great Expectations project within a Virtual Environment
- Add Snowflake tables to the project
- Create data profiles and expectation suites for the specified input tables.

**Note**: Before running any Makefile targets, ensure the `.env` file is properly configured and the desired input tables are listed in `config.yaml`.

Feel free to reach out if you encounter any issues or have questions about the process. Happy data profiling!
```
