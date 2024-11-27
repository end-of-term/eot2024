# cleaner/purge_ignores.py
import csv
from pathlib import Path
from urllib.parse import urlparse
from .utils.logging import logger

def load_ignore_list(file_path):
    """Load ignore list from a CSV file."""
    if not file_path.exists():
        logger.warning(f"Ignore file {file_path.relative_to(Path.cwd())} does not exist. Skipping filtering step.")
        return set()
    logger.info(f"Loading ignore list from {file_path.relative_to(Path.cwd())}...")
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        ignore_list = {row[0].strip().lower().rstrip(",") for row in reader if row}
    logger.info(f"Loaded {len(ignore_list)} entries from ignore list.")
    return ignore_list

def is_ignored(domain, ignore_list):
    """Check if the domain or any of its subdomains are in the ignore list."""
    parts = domain.split('.')
    for i in range(len(parts)):
        candidate = '.'.join(parts[i:])
        if candidate in ignore_list:
            return True
    return False

def filter_urls_and_domains(urls_file, domains_file, ignore_list):
    """Filter out URLs and domains that match or are subdomains of the ignore list."""
    logger.info("Filtering URLs and domains based on ignore list...")
    # Filter URLs
    filtered_urls = []
    with open(urls_file, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            url = row["url"].strip().lower()
            domain = urlparse(url).netloc
            if not is_ignored(domain, ignore_list):
                filtered_urls.append(row)
    # Save filtered URLs
    logger.info(f"Filtered {len(filtered_urls)} URLs. Saving to {urls_file.relative_to(Path.cwd())}.")
    with open(urls_file, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(filtered_urls)

    # Filter Domains
    filtered_domains = []
    with open(domains_file, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            domain = row["domain"].strip().lower()
            if not is_ignored(domain, ignore_list):
                filtered_domains.append(row)
    # Save filtered Domains
    logger.info(f"Filtered {len(filtered_domains)} domains. Saving to {domains_file.relative_to(Path.cwd())}.")
    with open(domains_file, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(filtered_domains)
    logger.info("Purge completed successfully.")
