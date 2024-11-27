# cleaner/urls.py
from collections import Counter
import re
import validators
from urllib.parse import urlparse, urlunparse

# Regex for URLs
URL_REGEX = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

def clean_url(url):
    """
    Remove unnecessary fragments or trailing characters and normalize the URL.
    """
    return normalize_url(url.split(",")[0])

def extract_urls_and_domains(file_path):
    """
    Extract and clean both URLs and standalone domains from a file.
    Returns two Counter objects: one for URLs and one for domains.
    """
    url_counter = Counter()
    domain_counter = Counter()
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            # Extract URLs
            matches = URL_REGEX.findall(line)
            for match in matches:
                cleaned_url = clean_url(match)
                if validators.url(cleaned_url):
                    url_counter[cleaned_url] += 1

            # Extract standalone domains
            words = line.split()
            for word in words:
                if validators.domain(word):
                    domain = word.lower()  # Normalize to lowercase
                    domain_counter[domain] += 1
    return url_counter, domain_counter

def normalize_url(url):
    """
    Normalize a URL:
    - Remove trailing slashes
    - Convert to lowercase
    """
    parsed_url = urlparse(url)
    normalized = parsed_url._replace(
        path=parsed_url.path.rstrip('/'),  # Remove trailing slash
    )
    return urlunparse(normalized).lower()
