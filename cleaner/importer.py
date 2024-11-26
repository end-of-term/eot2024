# cleaner/importer.py
import yaml
import requests
import os
import csv
from .utils import logger

def fetch_and_save_imports(config_path: str):
    """
    Reads the config YAML file, fetches files from specified URLs, processes them, and saves to the specified paths.
    :param config_path: Path to the YAML configuration file.
    """
    try:
        # Load the configuration file
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        imports = config.get('imports', {})
        if not imports:
            logger.warning("No 'imports' section found in the configuration file.")
            return
        for key, value in imports.items():
            url = value.get('url')
            path = value.get('path')
            filter_rules = value.get('filter', {})
            remove_rules = value.get('remove', {})
            if not url or not path:
                logger.error(f"Missing 'url' or 'path' for import '{key}'. Skipping.")
                continue
            # Fetch the data from the URL
            logger.info(f"Fetching data from {url}...")
            response = requests.get(url)
            response.raise_for_status()

            # Ensure the target directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # Save the raw data to the specified path
            with open(path, 'wb') as output_file:
                output_file.write(response.content)
            logger.debug(f"Raw data saved to {path}.")

            # Load filtered data if necessary
            # Process the file if removal rules are provided
            if filter_rules or remove_rules:
                logger.info(f"Processing file with filter and/or removal rules for import '{key}'...")
                process_file(path, remove_rules, filter_rules)
        logger.info("All imports processed successfully.")
    except Exception as e:
        logger.critical(f"An error occurred: {e}")

def process_file(file_path, remove_rules, filter_rules=None):
    """
    Processes the file to filter it and apply line/content removal rules.
    :param file_path: Path to the file to process.
    :param remove_rules: Dictionary containing removal rules.
    :param filter_rules: Dictionary containing filtering rules.
    """
    try:
        # Step 1: Read the content of the file
        with open(file_path, 'r') as file:
            content = file.readlines()
        logger.debug(f"File read successfully: {file_path} with {len(content)} lines.")

        # Step 2: Apply filtering rules, if any
        if filter_rules:
            processed_lines = []
            column_name = filter_rules['by_column']['column_name']
            accepted_values = filter_rules['by_column']['values']
            header = content[0].strip().split(",")
            if column_name in header:
                column_index = header.index(column_name)

                # Add headers before filtering
                processed_lines.append(content[0].strip())

                # Filter lines based on column values
                for line in content[1:]:
                    columns = line.strip().split(",")
                    if len(columns) > column_index and columns[column_index].strip() in accepted_values:
                        processed_lines.append(line.strip())
            logger.info(f"Filtered {len(processed_lines) - 1} rows based on rules.")
            content = processed_lines

        # Step 3: Apply removal rules
        line_start = remove_rules.get("line_start")
        trailing_content = remove_rules.get("trailing_content")
        final_lines = []

        for line in content:
            line = line.strip()
            if line_start and line.startswith(line_start):
                logger.debug(f"Removed line starting with '{line_start}': {line[:50]}...")
                continue
            if trailing_content and trailing_content in line:
                line = line.split(trailing_content)[0] + trailing_content
            if line:
                final_lines.append(line)

        logger.info(f"File processed with {len(final_lines)} lines remaining after applying removal rules.")

        # Step 4: Write the processed lines back to the file
        with open(file_path, 'w') as file:
            file.write("\n".join(final_lines))
        logger.info(f"File processed and saved: {file_path}")
    except Exception as e:
        logger.error(f"Error processing file: {e}")
