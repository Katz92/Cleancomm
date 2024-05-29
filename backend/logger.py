import logging
from logging.handlers import RotatingFileHandler

# Set maxBytes to 5 megabytes
max_bytes_in_megabytes = 10
max_bytes = max_bytes_in_megabytes * 1024 * 1024

# Set up logging configuration for Uvicorn access
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger_handler = RotatingFileHandler('app_access.log', maxBytes=max_bytes, backupCount=3)
uvicorn_access_logger_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
uvicorn_access_logger.addHandler(uvicorn_access_logger_handler)
uvicorn_access_logger.setLevel(logging.INFO)

# Set up logging configuration for Uvicorn errors
uvicorn_errors_logger = logging.getLogger("uvicorn.error")
uvicorn_errors_logger_handler = RotatingFileHandler('app_errors.log', maxBytes=max_bytes, backupCount=3)
uvicorn_errors_logger_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
uvicorn_errors_logger.addHandler(uvicorn_errors_logger_handler)
uvicorn_errors_logger.setLevel(logging.INFO)
