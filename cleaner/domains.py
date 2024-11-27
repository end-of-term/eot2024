# cleaner/domains.py
from urllib.parse import urlparse
from collections import Counter
import validators

def extract_domains(urls):
    """
    Extract and normalize domains from URLs, count occurrences.
    Returns a Counter object with domains.
    """
    domain_counter = Counter()
    for url, count in urls.items():
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()  # Normalize to lowercase
        if domain:
            # Remove leading 'www.' for normalization
            domain = domain.lstrip("www.")
            if validators.domain(domain):
                domain_counter[domain] += count
    return domain_counter
