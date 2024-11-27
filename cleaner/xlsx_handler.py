# cleaner/xlsx_handler.py
from .urls import extract_urls_and_domains, normalize_url, URL_REGEX
from collections import Counter
import pandas as pd
import validators
from urllib.parse import urlparse
from .utils.logging import logger

def process_xlsx_file(file_path):
    """
    Extract URLs and domains from an .xlsx file.
    Reuses existing logic from `urls.py` to avoid duplication.
    """
    url_counter = Counter()
    domain_counter = Counter()
    try:
        # Load the Excel file
        data = pd.read_excel(file_path)

        # Iterate through all columns and rows in the file
        for column in data.columns:
            for value in data[column].dropna():
                # Check if the value is a string to process URLs
                if isinstance(value, str):
                    # Extract URLs using existing regex
                    matches = URL_REGEX.findall(value)
                    for match in matches:
                        cleaned_url = normalize_url(match)
                        if validators.url(cleaned_url):
                            url_counter[cleaned_url] += 1

                    # Extract standalone domains
                    words = value.split()
                    for word in words:
                        if validators.domain(word):
                            domain = urlparse(word).netloc.lower()  # Normalize to lowercase
                            domain_counter[domain] += 1

        logger.info(f"Processed .xlsx file {file_path} successfully.")
        return url_counter, domain_counter
    except Exception as e:
        logger.error(f"Error processing .xlsx file {file_path}: {e}")
        return Counter(), Counter()
