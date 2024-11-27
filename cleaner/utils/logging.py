# cleaner/utils/logging.py
import logging
import os
import time
from logging.handlers import RotatingFileHandler
import json
import re
import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import threading
import queue

UNFUN_LOGGER_NAME = "Tree's Phone"
FUN_MOJIS = "🌳📞"
LOGGER_NAME = f"{UNFUN_LOGGER_NAME} {FUN_MOJIS}"

# Tree Paine NEVER misses a message... IYKYK

# Emoji map for log levels
LOG_EMOJIS = {
    "DEBUG": "🐛",
    "INFO": "💬",
    "WARNING": "🚧",
    "ERROR": "❌",
    "CRITICAL": "🔥",
}


# Initialize the logger
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)  # Default level

def fun_police(unfun_logger_name):
    # Remove special characters and replace spaces with underscores
    reptv_case_name = re.sub(r'[^a-zA-Z0-9\s]', '', unfun_logger_name)
    reptv_case_name = re.sub(r'\s+', '_', reptv_case_name)
    return reptv_case_name.lower()

def log_exception(exc_type, exc_value, exc_traceback):
    """
    Logs an exception with its traceback.
    """
    logger.error(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )

def test_logger():
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

class EmojiFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, tz=None, log_fun=False):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.tz = tz or timezone.utc
        self.log_fun = log_fun

    def format(self, record):
        if self.log_fun:
            # Using fixed width for emojis and levels for alignment
            emoji = LOG_EMOJIS.get(record.levelname, '')
            formatted_level = f"{emoji} {record.levelname}"
            # Align the total string length
            record.levelname = f"{formatted_level:<11}"
        else:
            record.levelname = f"{record.levelname:<8}"
        return super().format(record)

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=self.tz)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.isoformat()

class JsonFormatter(logging.Formatter):
    def __init__(self, tz=None):
        super().__init__()
        self.tz = tz or timezone.utc

    def format(self, record):
        record_dict = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "file": record.filename,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage()
        }
        return json.dumps(record_dict, ensure_ascii=False)

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=self.tz)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.isoformat()

def configure_logger():
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_fun = os.environ.get("LOG_FUN", "False").lower() == "true"
    log_verbose = os.environ.get("LOG_VERBOSE", "False").lower() == "true"
    log_files = os.environ.get("LOG_FILES", "False").lower() == "true"
    LOG_FILE_TYPE = os.environ.get("LOG_FILE_TYPE", "text").lower()
    LOG_PATH = os.environ.get("LOG_PATH", "logs")
    LOG_TIMEZONE = os.environ.get("LOG_TIMEZONE", "America/New_York")

    # Set up timezone
    try:
        tz = ZoneInfo(LOG_TIMEZONE)
    except ZoneInfoNotFoundError:
        print(f"Timezone '{LOG_TIMEZONE}' not found. Defaulting to UTC.")
        tz = timezone.utc

    # Clear existing handlers to prevent duplication
    logger.handlers = []
    logger.setLevel(level)
    # Set up formatters
    fmt, datefmt = get_formatters(log_verbose)
    # Set up the queue for asynchronous logging
    log_queue = queue.Queue(-1)
    # Set up handlers
    handlers = []
    # Console handler
    shell_handler = setup_console_handler(level, fmt, datefmt, tz, log_fun)
    handlers.append(shell_handler)
    # File logging configuration
    if log_files:
        file_handlers = setup_file_handlers(level, fmt, datefmt, tz, LOG_FILE_TYPE, LOG_PATH, log_verbose)
        handlers.extend(file_handlers)
        # Start a thread to monitor date changes
        date_monitor = threading.Thread(
            target=monitor_date_change,
            args=(handlers, level, LOG_PATH, LOG_FILE_TYPE, tz, log_verbose)
        )
        date_monitor.daemon = True  # Daemonize thread
        date_monitor.start()

    # Set up the QueueHandler for asynchronous logging
    queue_handler = logging.handlers.QueueHandler(log_queue)
    logger.addHandler(queue_handler)

    # Start the QueueListener with the handlers
    listener = logging.handlers.QueueListener(log_queue, *handlers)
    listener.start()

    # Store listener for later shutdown
    logger.listener = listener

    # Set up exception logging
    sys.excepthook = log_exception

    # For testing purposes
    test_logger()

def get_formatters(log_verbose):
    if log_verbose:
        fmt = "%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s"
        datefmt = '%Y-%m-%d %H:%M:%S %Z'
    else:
        fmt = "%(levelname)-8s %(message)s"
        datefmt = None
    return fmt, datefmt

def setup_console_handler(level, fmt, datefmt, tz, log_fun):
    shell_handler = logging.StreamHandler()
    shell_handler.setLevel(level)
    shell_formatter = EmojiFormatter(fmt, datefmt=datefmt, tz=tz, log_fun=log_fun)
    shell_handler.setFormatter(shell_formatter)
    return shell_handler

def setup_file_handlers(level, fmt, datefmt, tz, LOG_FILE_TYPE, LOG_PATH, log_verbose):
    # Create the logs directory if it doesn't exist
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

    REALLY_UNFUN_LOGGER_NAME = fun_police(UNFUN_LOGGER_NAME)
    current_date = time.strftime('%Y-%m-%d')

    file_handlers = []

    if LOG_FILE_TYPE in ('text', 'all'):
        text_filename = f"{LOG_PATH}/{REALLY_UNFUN_LOGGER_NAME}-{current_date}.log"
        text_file_handler = RotatingFileHandler(
            filename=text_filename,
            mode='a',
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=3,
            encoding='utf-8',
            delay=0
        )
        text_file_handler.setLevel(level)
        text_formatter = TimezoneFormatter(fmt, datefmt=datefmt, tz=tz)
        text_file_handler.setFormatter(text_formatter)
        file_handlers.append(text_file_handler)

    if LOG_FILE_TYPE in ('json', 'all'):
        json_filename = f"{LOG_PATH}/{REALLY_UNFUN_LOGGER_NAME}-{current_date}.json"
        json_file_handler = RotatingFileHandler(
            filename=json_filename,
            mode='a',
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=3,
            encoding='utf-8',
            delay=0
        )
        json_file_handler.setLevel(level)
        json_formatter = JsonFormatter(tz=tz)
        json_file_handler.setFormatter(json_formatter)
        file_handlers.append(json_file_handler)

    return file_handlers

def monitor_date_change(handlers, level, LOG_PATH, LOG_FILE_TYPE, tz, log_verbose):
    current_date = time.strftime('%Y-%m-%d')
    while True:
        time.sleep(60)  # Check every minute
        new_date = time.strftime('%Y-%m-%d')
        if new_date != current_date:
            current_date = new_date
            # Update file handlers
            update_file_handlers(handlers, level, LOG_PATH, LOG_FILE_TYPE, current_date, tz, log_verbose)

def update_file_handlers(handlers, level, LOG_PATH, LOG_FILE_TYPE, current_date, tz, log_verbose):
    REALLY_UNFUN_LOGGER_NAME = fun_police(UNFUN_LOGGER_NAME)
    new_handlers = []
    fmt, datefmt = get_formatters(log_verbose)
    if LOG_FILE_TYPE in ('text', 'all'):
        text_filename = f"{LOG_PATH}/{REALLY_UNFUN_LOGGER_NAME}-{current_date}.log"
        text_file_handler = RotatingFileHandler(
            filename=text_filename,
            mode='a',
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8',
            delay=0
        )
        text_file_handler.setLevel(level)
        text_formatter = TimezoneFormatter(fmt, datefmt=datefmt, tz=tz)
        text_file_handler.setFormatter(text_formatter)
        new_handlers.append(text_file_handler)

    if LOG_FILE_TYPE in ('json', 'all'):
        json_filename = f"{LOG_PATH}/{REALLY_UNFUN_LOGGER_NAME}-{current_date}.json"
        json_file_handler = RotatingFileHandler(
            filename=json_filename,
            mode='a',
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8',
            delay=0
        )
        json_file_handler.setLevel(level)
        json_formatter = JsonFormatter(tz=tz)
        json_file_handler.setFormatter(json_formatter)
        new_handlers.append(json_file_handler)

    # Remove old file handlers from handlers list and close them
    for handler in handlers[:]:
        if isinstance(handler, RotatingFileHandler):
            handlers.remove(handler)
            handler.close()

    # Add new handlers to the handlers list
    handlers.extend(new_handlers)
    # Reconfigure the QueueListener with new handlers
    logger.listener.handlers = handlers
    logger.info(f"Log file updated to date: {current_date}")

def get_logger(name=None):
    if name is None:
        name = LOGGER_NAME
    return logging.getLogger(name)

# Log statements for testing purposes
if __name__ == "__main__":
    configure_logger()
    test_logger()
