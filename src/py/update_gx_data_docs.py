import logging
import os
import re
import sys
from datetime import datetime

import common
from bs4 import BeautifulSoup
from jinja2 import Environment
from jinja2 import FileSystemLoader

# Set up a specific logger with our desired output level
logger = common.get_logger(log_level=logging.DEBUG)

# ---------------------
# Constants
# ---------------------
# filepath-specific
# ---------------------
CURRENT_DATE_STR = datetime.now().strftime("%Y%m%d")
SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
TEMPLATES_DIR = os.path.join(PROJECT_DIR, "src", "templates", "jinja_templates")
PYTHON_SCRIPTS_DIR = os.path.join(PROJECT_DIR, "src", "py")
# ---------------------
# Other
# ---------------------
GX_DATA_DOCS_HTML_FILE = "gx/uncommitted/data_docs/local_site/index.html"


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


def setup_jinja_template(ip_jinja_template_file):
    """Set up/get the Jinja template"""
    jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
    return jinja_env.get_template(ip_jinja_template_file)


def read_target_html_from_file(file_path):
    try:
        with open(file_path, encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logger.debug(f"ERROR: An error occurred while reading the input file: {e}")
        sys.exit()


def prettify_html(input_file):
    try:
        with open(input_file, encoding="utf-8") as file:
            html_content = file.read()

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Prettify the HTML content for formatting
        prettified_html = soup.prettify()

        # Save the prettified HTML content to a new file
        with open(input_file, "w", encoding="utf-8") as file:
            file.write(prettified_html)

        return prettified_html

    except Exception as e:
        logger.debug(f"ERROR: An error occurred while processing the input HTML: {e}")
        sys.exit()


def find_and_replace_html_code(input_file):
    try:
        # Prettify the HTML content and get the prettified HTML
        prettified_html = prettify_html(input_file)

        # -------------------------------------
        # String pattern declarations
        # -------------------------------------
        # HTML code pattern to find
        html_pattern = r"</script>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*<footer>\s*<p>\s*Stay current on everything GX with our newsletter"  # noqa

        # JavaScript code pattern to find
        js_pattern = r'\$\(document\)\.ready\(function\(\)\s*\{\s*\$\("#section-1-content-block-2-2-body-table"\)\.on\(\'click-row\.bs\.table\',\s*function\(e,\s*row,\s*\$element\)\s*\{\s*window\.location\s*=\s*\$element\.data\("href"\);\s*\}\)\s*}\s*\);\s*'  # noqa

        # Combined JavaScript/HTML code pattern
        combined_html_pattern = js_pattern + html_pattern

        # -------------------------------------
        # Pattern matching/check functions
        # -------------------------------------
        # Search for subsequent HTML content
        html_check_match = re.search(html_pattern, prettified_html, re.DOTALL)
        # Search for the specific JavaScript content
        js_match = re.search(js_pattern, prettified_html, re.DOTALL)
        # search for the above 2 variables combined
        combined_html_pattern_match = re.search(combined_html_pattern, prettified_html, re.DOTALL)

        # ----------------------------------------
        # Error handling for pattern matching
        # ----------------------------------------
        if html_check_match:
            logger.debug("SUCCESS: Subsequent HTML elements found in the file.")
        else:
            logger.debug("ERROR: Subsequent HTML elements not found in the file.")
            sys.exit()

        if js_match:
            specific_js_code = js_match.group()
            logger.debug("SUCCESS: Specific JavaScript code found in the HTML file.")
            logger.debug(specific_js_code)
        else:
            logger.error("ERROR: Specific JavaScript content not found in the HTML file.")
            sys.exit()

        # Check if combined pattern is true
        if combined_html_pattern_match:
            logger.debug("SUCCESS: Combined JavaScript and HTML patterns found in the file.")

            # Read in the replacement HTML content (to replace the pattern) from a text file
            target_html = read_target_html_from_file(os.path.join(PYTHON_SCRIPTS_DIR, "txt/target_html.txt"))

            # Perform find and replace operation
            updated_html_file = re.sub(combined_html_pattern, target_html, prettified_html, flags=re.DOTALL)
            updated_html_file = re.sub(combined_html_pattern, target_html, prettified_html, flags=re.DOTALL)

            # Save the modified HTML content to the input file
            with open(input_file, "w", encoding="utf-8") as file:
                file.write(updated_html_file)

            # Parse the updated HTML content using BeautifulSoup for final consistent formatting
            prettify_html(input_file)

            # Output success message
            logger.debug("SUCCESS: HTML processing and pattern replacement completed.")
        else:
            logger.error("ERROR: Combined JavaScript and HTML patterns not found in the file.")
            sys.exit()

    except Exception as e:
        logger.error(f"ERROR: An error occurred during HTML processing and pattern replacement: {e}")
        sys.exit()


if __name__ == "__main__":
    # main()
    find_and_replace_html_code(GX_DATA_DOCS_HTML_FILE)
