# cleaner/__init__.py
from collections import Counter
from .config import load_config
from .urls import extract_urls_and_domains, normalize_url
from .domains import extract_domains
from .file_io import save_to_csv
from .purge_ignores import load_ignore_list, filter_urls_and_domains
from pathlib import Path
from .utils.logging import logger

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "seed-lists"
OUTPUT_DIR = BASE_DIR / "output"
IGNORE_FILE = OUTPUT_DIR / "ignore_domains.csv"

def process_files():
    """Main processing function."""
    logger.info("Starting file processing...")
    config = load_config()
    output_config = config.get("output", {})

    # Get file paths and sorting configs
    urls_config = output_config.get("urls", {})
    domains_config = output_config.get("domains", {})

    urls_path = OUTPUT_DIR / urls_config.get("path", "urls.csv")
    domains_path = OUTPUT_DIR / domains_config.get("path", "domains.csv")

    url_counter = Counter()
    standalone_domain_counter = Counter()

    # Process files
    logger.debug("Scanning input directory for files...")
    files = list(INPUT_DIR.glob("**/*"))  # Gather all files to process
    total_files = len([f for f in files if f.is_file()])
    logger.info(f"Found {total_files} files in the input directory.")

    processed_files = 0
    for file in files:
        if file.is_file():
            relative_file = file.relative_to(BASE_DIR)
            logger.debug(f"Processing file: {relative_file}")
            file_urls, file_domains = extract_urls_and_domains(file)
            # Normalize URLs before counting
            normalized_urls = {normalize_url(url): count for url, count in file_urls.items()}
            url_counter.update(normalized_urls)
            standalone_domain_counter.update(file_domains)

            processed_files += 1
            if processed_files % 10 == 0 or processed_files == total_files:
                logger.info(f"Processed {processed_files}/{total_files} files...")

    logger.info("Finished processing files.")
    logger.info(f"Extracted {len(url_counter)} unique URLs and {len(standalone_domain_counter)} standalone domains.")

    logger.info("Saving URLs to output file...")
    # Save URLs with counts (apply urls_config sort)
    save_to_csv(urls_path, url_counter, ["url", "count"], urls_config.get("sort"))
    logger.info(f"URLs saved to {urls_path.relative_to(BASE_DIR)}")

    # Combine URL-derived domains and standalone domains
    logger.info("Extracting and saving domains...")
    domain_counter = extract_domains(url_counter)
    domain_counter.update(standalone_domain_counter)
    save_to_csv(domains_path, domain_counter, ["domain", "count"], domains_config.get("sort"))
    logger.info(f"Domains saved to {domains_path.relative_to(BASE_DIR)}")

    # Purge ignored entries
    ignore_list = load_ignore_list(IGNORE_FILE)
    if ignore_list:
        filter_urls_and_domains(urls_path, domains_path, ignore_list)

    logger.info("File processing complete.")
