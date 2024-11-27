# cleaner/__main__.py
from . import process_files
from .utils import logger, configure_logger
from .update_ignore import update_ignore_file
from .importer import fetch_and_save_imports

if __name__ == "__main__":
    configure_logger()
    logger.info("Logger setup")

    # Run data import process
    config_path = "config/main.yml"
    logger.info("Starting data import process...")
    fetch_and_save_imports(config_path)

    # Update Ignore File
    update_ignore_file()

    process_files()
