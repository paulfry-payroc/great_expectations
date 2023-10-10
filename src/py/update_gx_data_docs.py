import os
import sys
from datetime import datetime

import common
from jinja2 import Environment
from jinja2 import FileSystemLoader

# Set up a specific logger with our desired output level
logger = common.get_logger()

# Constants
CURRENT_DATE_STR = datetime.now().strftime("%Y%m%d")
SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
TEMPLATES_DIR = os.path.join(PROJECT_DIR, "src", "templates", "jinja_templates")


def setup_jinja_template(ip_jinja_template_file):
    """Set up/get the Jinja template"""
    jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
    return jinja_env.get_template(ip_jinja_template_file)


def main():
    try:
        input_tables, other_params = common.load_config_from_yaml()
        logger.debug(f"input tables = {input_tables}")

        jinja_template = setup_jinja_template("index.html.j2")
        template_path = os.path.join(TEMPLATES_DIR, "index.html.j2")

        target_dir = os.path.join(PROJECT_DIR, "gx", "uncommitted", "data_docs", "local_site")

        # # Validate the Jinja template
        if not os.path.exists(template_path):
            logger.error(f"Error: Jinja template '{jinja_template}' not found.")
            sys.exit(1)

        with open(os.path.join(target_dir, "abc.html"), "w") as op_file:
            op_file.write(jinja_template.render(input_tables=input_tables, current_data_str=CURRENT_DATE_STR))

    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
