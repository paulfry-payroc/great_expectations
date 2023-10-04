import great_expectations as ge

context = ge.data_context.DataContext("/path/to/your/great_expectations/directory")
my_snowflake_batch = context.get_batch(
    {
        "batch_kwargs": {
            "table": "BKP_CHANGE_HISTORY",
            "datasource": "my_snowflake_store",
            "limit": 1000,
        },  # Adjust the limit as needed for profiling
        "expectation_suite_name": "my_suite_name",  # Choose a suitable name for your expectation suite
    }
)
my_snowflake_batch.profile()
