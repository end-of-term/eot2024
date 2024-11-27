# cleaner/update_ignore.py
import os
from .utils import logger

def update_ignore_file():
    # Define the directory containing the text files
    directory = 'config/domain_ignores'
    # Initialize a set to hold unique domain names
    unique_domains = set()
    # Iterate over all text files in the specified directory
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            filepath = os.path.join(directory, filename)
            # Open and read each file
            with open(filepath, 'r') as file:
                # Add lines to the set (sets automatically handle duplicate values)
                for line in file:
                    domain = line.strip()
                    if domain:
                        unique_domains.add(domain)
    # Specify the output file's path
    output_file = 'output/ignore_domains.csv'
    # Write the unique domain names to a CSV file
    with open(output_file, 'w') as txtfile:
        txtfile.write("domain,\n")
        # Write each domain from the set into the file, one per line
        for domain in sorted(unique_domains):
            if not domain.endswith(','):
                domain += ','
            txtfile.write(f"{domain}\n")
    logger.info(f'✅ Unique domains have been written to {output_file}')
