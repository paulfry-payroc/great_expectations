#!/usr/bin/env python3
"""
Python Version  : 3.8
* Name          : modify_html.py
* Description   : Collection of functions to modify generated html content
* Created       : 26-02-2021
* Usage         : python3 modify_html.py
"""

__author__ = "Paul Fry"
__version__ = "1.0"


import os
import sys
import re
import common
from bs4 import BeautifulSoup

# Set up logging
logger = common.get_logger()


# Filepath-specific vars
SCRIPT_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
TEMPLATES_DIR = os.path.join(PROJECT_DIR, "src", "templates", "jinja_templates")
PYTHON_SCRIPTS_DIR = os.path.join(PROJECT_DIR, "src", "py")

# Other vars
GX_DATA_DOCS_DIR = "gx/uncommitted/data_docs/local_site/"
GX_DATA_DOCS_HTML_FILE = os.path.join(GX_DATA_DOCS_DIR, "index.html")
HTML_JINJA_TEMPLATE = os.path.join(TEMPLATES_DIR, "index.html.j2")


def modify_html_content_patterns():
    """Processes the input HTML file, identifies specific patterns, and replaces them with new content."""
    try:
        # Prettify the HTML content and get the prettified HTML
        html_content = prettify_html(GX_DATA_DOCS_HTML_FILE)

        # fetch the html pattern
        combined_html_pattern, combined_html_pattern_match = validate_html_patterns(html_content)

        # Check if combined pattern is true
        if combined_html_pattern_match:
            logger.debug("SUCCESS: Combined JavaScript and HTML patterns found in the file.")

            # Read in the replacement HTML content (to replace the pattern) from a text file
            target_html = read_target_html_from_file(os.path.join(PYTHON_SCRIPTS_DIR, "txt/target_html.txt"))

            # Perform find and replace to enable data profiling content to be shown/rendered
            updated_html_file = re.sub(combined_html_pattern, target_html, html_content, flags=re.DOTALL)

            # write output to html files
            write_output_to_html(updated_html_file)

            # Output success message
            logger.debug("SUCCESS: HTML processing and pattern replacement completed.")
        else:
            logger.error("ERROR: Combined JavaScript and HTML patterns not found in the file.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"ERROR: An error occurred during HTML processing and pattern replacement: {e}")
        sys.exit(1)


def prettify_html(input_file):
    """Prettifies the HTML content from the input file using BeautifulSoup, preserving formatting and structure."""
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
        sys.exit(1)


def validate_html_patterns(html_content):
    """Checks if specific HTML patterns exist within the given HTML content and returns the combined pattern and match object."""
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
    html_check_match = re.search(html_pattern, html_content, re.DOTALL)
    # Search for the specific JavaScript content
    js_match = re.search(js_pattern, html_content, re.DOTALL)
    # search for the above 2 variables combined
    combined_html_pattern_match = re.search(combined_html_pattern, html_content, re.DOTALL)

    # ----------------------------------------
    # Error handling for pattern matching
    # ----------------------------------------
    if html_check_match:
        logger.debug("SUCCESS: Subsequent HTML elements found in the file.")
    else:
        logger.error("ERROR: Subsequent HTML elements not found in the file.")
        sys.exit(1)

    if js_match:
        specific_js_code = js_match.group()
        logger.debug("SUCCESS: Specific JavaScript code found in the HTML file.")
        logger.debug(specific_js_code)
    else:
        logger.error("ERROR: Specific JavaScript content not found in the HTML file.")
        sys.exit(1)

    return combined_html_pattern, combined_html_pattern_match


def read_target_html_from_file(file_path):
    """Reads the content of the target HTML file from the specified file path and returns it as a string."""
    try:
        with open(file_path, encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logger.debug(f"ERROR: An error occurred while reading the input file: {e}")
        sys.exit(1)


def write_output_to_html(updated_html_file):
    """Writes the updated HTML content to 'index.html' and 'index.html.j2', ensuring consistent formatting for Jinja rendering."""
    # we want to write 2 versions of the newly updated file out:
    # index.html & index.html.j2 - as we need this for jinja-rendering in the function 'add_data_profiling_content()'
    html_op_files = [GX_DATA_DOCS_HTML_FILE, HTML_JINJA_TEMPLATE]

    for html_file in html_op_files:
        try:
            with open(html_file, "w") as file:  # Save the modified HTML content to the input file
                file.write(updated_html_file)

            # Parse the updated HTML content using BeautifulSoup for final consistent formatting
            prettify_html(html_file)
        except Exception as e:
            logger.error(f"Error occurred while writing {html_file}: {e}")
            sys.exit(1)


def modify_html_tabs_content(file_path):
    """Modifies the specified HTML file content, replacing the specified text."""

    # Validate if the input file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read the content of the HTML file
    with open(file_path) as file:
        html_content = file.read()

    # The old/existing html pattern/content to find
    old_html_pattern = r'<li class="nav-item">\s*<a\s*aria-controls="Expectation-Suites"\s*aria-selected="false"\s*class="nav-link"\s*data-toggle="tab"\s*href="#Expectation-Suites"\s*id="Expectation-Suites-tab"\s*role="tab">\s*Expectation Suites\s*</a>\s*</li>'  # noqa
    # Read in the replacement HTML pattern/content from a text file
    new_html_pattern = read_target_html_from_file(os.path.join(PYTHON_SCRIPTS_DIR, "txt/target_html_tabs.txt"))

    # Check if the pattern exists in the html content
    if re.search(old_html_pattern, html_content, re.DOTALL):
        # Perform find and replace operation
        updated_html_file = re.sub(old_html_pattern, new_html_pattern, html_content, flags=re.DOTALL)

        # Write the modified content back to the file
        with open(file_path, "w") as file:
            file.write(updated_html_file)

        logger.debug(f"Text substitution successful in {file_path}")
    else:
        logger.error(f"No substitution made in {file_path}")
        sys.exit(1)
