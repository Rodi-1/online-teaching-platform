"""
Structured JSON Logging Configuration
This module provides centralized logging configuration for the microservice.
"""
import logging
import sys
from typing import Any, Dict

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds service-specific fields to all log records.
    """
    
    def __init__(self, *args, service_name: str = "unknown-service", **kwargs):
        self.service_name = service_name
        super().__init__(*args, **kwargs)
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """
        Add custom fields to the log record.
        
        Args:
            log_record: The dictionary that will be logged as JSON
            record: The logging.LogRecord object
            message_dict: Dictionary from the log message
        """
        super().add_fields(log_record, record, message_dict)
        
        # Add standard fields
        log_record['timestamp'] = self.formatTime(record, self.datefmt)
        log_record['level'] = record.levelname
        log_record['service'] = self.service_name
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        
        # Ensure message is always present
        if 'message' not in log_record:
            log_record['message'] = record.getMessage()


def setup_logging(
    service_name: str,
    log_level: str = "INFO",
    log_format: str = "%(timestamp)s %(level)s %(service)s %(logger)s %(message)s"
) -> logging.Logger:
    """
    Setup structured JSON logging for the service.
    
    Args:
        service_name: Name of the microservice
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format string (not used for JSON but kept for compatibility)
    
    Returns:
        Configured logger instance
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set log level
    log_level_obj = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(log_level_obj)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_obj)
    
    # Create JSON formatter
    json_formatter = CustomJsonFormatter(
        service_name=service_name,
        datefmt="%Y-%m-%dT%H:%M:%S.%fZ"
    )
    console_handler.setFormatter(json_formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Configure uvicorn loggers to use the same format
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.addHandler(console_handler)
        logger.propagate = False
    
    # Log initialization
    root_logger.info(
        "Logging initialized",
        extra={
            "service": service_name,
            "log_level": log_level
        }
    )
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

