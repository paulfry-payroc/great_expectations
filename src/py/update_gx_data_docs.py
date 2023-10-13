import os
import shutil
import sys
from datetime import datetime

import common
import great_expectations as gx
import modify_html_functions
from jinja2 import Environment
from jinja2 import FileSystemLoader

# Set up logging
logger = common.get_logger()
# logger = common.get_logger(log_level=logging.DEBUG)

# ---------------------
# Filepath-specific vars
# ---------------------
SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
TEMPLATES_DIR = os.path.join(PROJECT_DIR, "src", "templates", "jinja_templates")
GX_DATA_DOCS_DIR = "gx/uncommitted/data_docs/local_site/"
GX_DATA_DOCS_HTML_FILE = os.path.join(GX_DATA_DOCS_DIR, "index.html")
# Other
CURRENT_DATE_STR = datetime.now().strftime("%Y%m%d")


def setup_jinja_template(ip_jinja_template_file):
    """Set up/get the Jinja template"""
    jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
    return jinja_env.get_template(ip_jinja_template_file)


def add_data_profiling_content():
    """Adds data profiling content to the HTML file using Jinja template, based on input tables and current date."""
    try:
        input_tables, other_params = common.load_config_from_yaml()
        logger.debug(f"input tables = {input_tables}")

        jinja_template = setup_jinja_template("index.html.j2")
        template_path = os.path.join(TEMPLATES_DIR, "index.html.j2")

        # Validate the Jinja template
        if not os.path.exists(template_path):
            logger.error(f"Error: Jinja template '{jinja_template}' not found.")
            sys.exit(1)

        with open(GX_DATA_DOCS_HTML_FILE, "w") as op_file:
            op_file.write(jinja_template.render(input_tables=input_tables, current_date_str=CURRENT_DATE_STR))

    except Exception as e:
        logger.error(f"\nAn error occurred: {e}")
        sys.exit(1)


def create_html_backup(file_path):
    """Creates a backup of the specified file."""
    backup_path = os.path.join(GX_DATA_DOCS_DIR, "bkp_index.html")
    try:
        shutil.copyfile(file_path, backup_path)
        logger.debug(f"Backup created: {backup_path}")
    except Exception as e:
        logger.error(f"Error creating backup: {e}")


def main():
    """Main function to execute the script."""
    try:
        # Check if the index.html file exists
        if os.path.exists(GX_DATA_DOCS_HTML_FILE):
            # Step 1: Create a backup of the original index.html file
            create_html_backup(GX_DATA_DOCS_HTML_FILE)

            # Step 2: Find and replace specific HTML and JavaScript patterns
            modify_html_functions.modify_html_content_patterns()

            # Step 3: Add data profiling content using Jinja templates
            add_data_profiling_content()

            # Step 4: Modify the HTML file content
            modify_html_functions.modify_html_tabs_content(GX_DATA_DOCS_HTML_FILE)

            # Step 5: Open the Great Expectations data documentation
            context = gx.get_context()  # Create a GX context
            context.open_data_docs()  # Open the GX 'data docs' (i.e., HTML file)
        else:
            # Log an error if the file doesn't exist
            logger.error(f"Error: File '{GX_DATA_DOCS_HTML_FILE}' not found.")
    except Exception as e:
        # Log any exceptions that occur during execution
        logger.error(f"\nAn error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
