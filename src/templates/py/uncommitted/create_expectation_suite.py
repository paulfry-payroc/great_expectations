import datetime

import great_expectations as gx
import great_expectations.jupyter_ux
import pandas as pd
from great_expectations.checkpoint import SimpleCheckpoint
from great_expectations.core.batch import BatchRequest
from great_expectations.exceptions import DataContextError

context = gx.get_context()

batch_request = {
    "datasource_name": "my_datasource",
    "data_connector_name": "default_configured_data_connector_name",
    "data_asset_name": "BKP_CHANGE_HISTORY",
    "limit": 1000,
}

expectation_suite_name = "v2_oct5th_post_lunch"

validator = context.get_validator(
    batch_request=BatchRequest(**batch_request),
    expectation_suite_name=expectation_suite_name,
)
column_names = [f'"{column_name}"' for column_name in validator.columns()]
print(f"Columns: {', '.join(column_names)}.")
validator.head(n_rows=5, fetch_all=False)

# 2. select columns
exclude_column_names = []

# 3. run the onboardingDataAssistant
result = context.assistants.onboarding.run(
    batch_request=batch_request,
    exclude_column_names=exclude_column_names,
)
validator.expectation_suite = result.get_expectation_suite(expectation_suite_name=expectation_suite_name)

# 4. save & review expectation suite

print(validator.get_expectation_suite(discard_failed_expectations=False))
validator.save_expectation_suite(discard_failed_expectations=False)

checkpoint_config = {
    "class_name": "SimpleCheckpoint",
    "validations": [
        {
            "batch_request": batch_request,
            "expectation_suite_name": expectation_suite_name,
        }
    ],
}
checkpoint = SimpleCheckpoint(
    f"{validator.active_batch_definition.data_asset_name}_{expectation_suite_name}",
    context,
    **checkpoint_config,
)
checkpoint_result = checkpoint.run()

context.build_data_docs()

validation_result_identifier = checkpoint_result.list_validation_result_identifiers()[0]
context.open_data_docs(resource_identifier=validation_result_identifier)
