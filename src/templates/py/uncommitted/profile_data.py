import pandas as pd
import snowflake.connector
from great_expectations.data_context.store import HtmlSiteStore
from great_expectations.dataset.pandas_dataset import PandasDataset
from great_expectations.profile.basic_dataset_profiler import BasicDatasetProfiler
from great_expectations.render.renderer import ExpectationSuitePageRenderer
from great_expectations.render.renderer import ProfilingResultsPageRenderer
from great_expectations.render.view import DefaultJinjaPageView

# import the renderer who will basically create the document content
# import the view template who will basically convert the document content to HTML

snowflake_params = {
    "account": "sp65314.us-east-2.aws",
    "user": "paul_fry",
    "password": "Carpet11!",
    "warehouse": "DEV_WH",
    "database": "DTE_PFRY",
    "schema": "DWH_WAREHOUSE",
}

conn = snowflake.connector.connect(
    account=snowflake_params["account"],
    user=snowflake_params["user"],
    password=snowflake_params["password"],
    warehouse=snowflake_params["warehouse"],
    database=snowflake_params["database"],
    schema=snowflake_params["schema"],
)

sql_query = "SELECT * FROM BKP_CHANGE_HISTORY"
snowflake_cursor = conn.cursor()
snowflake_cursor.execute(sql_query)
result = snowflake_cursor.fetchall()
snowflake_cursor.close()
conn.close()

column_names = [desc[0] for desc in snowflake_cursor.description]
df = pd.DataFrame(result, columns=column_names)

pandas_dataset = PandasDataset(df)

# profiling the data
# we will be using BasicDatasetProfiler as a profiler
expectation_suite_based_on_profiling, validation_result_based_on_profiling = pandas_dataset.profile(
    BasicDatasetProfiler
)

expectation_suite_based_on_profiling

## HTML bits below

# visualize the profiling result and expectation came from profiling

profiling_result_document_content = ProfilingResultsPageRenderer().render(validation_result_based_on_profiling)
# it is of type great_expectations.render.types.RenderedDocumentContent
expectation_based_on_profiling_document_content = ExpectationSuitePageRenderer().render(
    expectation_suite_based_on_profiling
)
# it is also of type great_expectations.render.types.RenderedDocumentContent

# we will generate the HTML
profiling_result_HTML = DefaultJinjaPageView().render(profiling_result_document_content)  # type string or str
expectation_based_on_profiling_HTML = DefaultJinjaPageView().render(expectation_based_on_profiling_document_content)

# Specify the base directory where the HTML files will be stored within the data documentation directory
base_url = "uncommitted/data_docs/local_site/"

# Specify the base directory where the HTML files will be stored within the data documentation directory
base_directory = "uncommitted/data_docs/local_site/"

profiling_results_path = "data_docs/local_site/profiling_results.html"
expectation_suite_path = "data_docs/local_site/expectation_suite.html"

# Write the raw HTML content to files
with open(profiling_results_path, "w") as profiling_results_file:
    profiling_results_file.write(profiling_result_HTML)

with open(expectation_suite_path, "w") as expectation_suite_file:
    expectation_suite_file.write(expectation_based_on_profiling_HTML)
