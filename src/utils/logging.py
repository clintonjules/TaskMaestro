import logging
from datetime import datetime
from pathlib import Path

def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create a unique log file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"ensemble_{timestamp}.log"
    
    # Create file handler for all logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    
    # Create console handler that excludes HTTP requests
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    # Add filter to exclude HTTP request logs
    console_handler.addFilter(lambda record: 'HTTP Request' not in record.getMessage())
    
    # Get the root logger and remove any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers = []
    
    # Configure root logger
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create a separate logger for HTTP requests
    http_logger = logging.getLogger('httpx')
    http_logger.setLevel(logging.INFO)
    http_logger.propagate = False  # Prevent HTTP logs from propagating to root logger
    http_logger.addHandler(file_handler)
    
    return root_logger 