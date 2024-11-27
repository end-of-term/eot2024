# EOT 2024 Cleaner

The `cleaner` module processes domain and URL data to extract, normalize, and filter information. It integrates with configurations for flexible input/output management and supports automated updates to ignore lists.

## Features
- Extract and normalize URLs and domains from input files.
- Save processed data to CSV files with configurable sorting.
- Filter URLs/domains using ignore lists.
- Automatically update ignore lists from configuration-defined sources.

## Basic Setup

### Configuration
1. **Main Config File**: Ensure `config/main.yml` exists and is correctly configured. This file defines:
   - Input file paths (`imports` section).
   - Ignore list rules (`domain_ignores`).
   - Output file paths and sorting (`output`).

2. **Ignore Lists**: Located in `config/domain_ignores/`. Update automatically via `update_ignore.py`.

### Input
Place seed lists in the `seed-lists/` directory. Supported formats include `.txt`, `.csv`, and `.xlsx`.

### Output
Processed data is saved in the `output/` directory:
- `urls.csv` - Extracted URLs.
- `domains.csv` - Normalized domains.
- `ignore_domains.csv` - Compiled ignore list.
- `seed-list.csv` - Final list of cleaned URLs.

## Usage
Run the module from the command line:
```bash
poetry run python -m cleaner
```

## What it does

    1.	Fetch and process seed files based on config/main.yml.
    2.	Extract and normalize URLs and domains.
    3.	Save results to output/.
    4.	Filter out ignored domains and URLs.
    5.	Generate `seed-list.csv` for cleaned URL output.

For logging and debugging, check the console output or logs configured in cleaner/utils/logging.py.

Everything runs via Github action.

