"""
Logging utilities for wetland analysis.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Default log format
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
    clear_handlers: bool = True
) -> logging.Logger:
    """
    Set up logging configuration.

    Parameters
    ----------
    level : int, optional
        Logging level (e.g., logging.INFO, logging.DEBUG)
    log_file : str, optional
        Path to log file. If None, log to console only.
    log_format : str, optional
        Log message format
    date_format : str, optional
        Date format in logs
    clear_handlers : bool, optional
        Whether to clear existing handlers

    Returns
    -------
    logging.Logger
        Root logger
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Clear existing handlers if requested
    if clear_handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(log_format, date_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file specified)
    if log_file:
        # Create directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get logger with specified name.

    Parameters
    ----------
    name : str
        Logger name (usually __name__)
    level : int, optional
        Logging level for this logger. If None, inherit from parent.

    Returns
    -------
    logging.Logger
        Logger instance
    """
    logger = logging.getLogger(name)

    if level is not None:
        logger.setLevel(level)

    return logger


def log_execution_info(
    logger: logging.Logger,
    function_name: str,
    parameters: Dict[str, Any],
    start_time: datetime
) -> None:
    """
    Log function execution information.

    Parameters
    ----------
    logger : logging.Logger
        Logger instance
    function_name : str
        Name of the function being executed
    parameters : dict
        Function parameters
    start_time : datetime
        Start time of execution
    """
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Log execution start
    logger.info(f"Executing {function_name}")
    logger.debug(f"Parameters: {parameters}")

    # Log execution end
    logger.info(f"Completed {function_name} in {duration:.2f} seconds")


def setup_performance_logging(
    log_file: str = 'performance.log',
    level: int = logging.INFO
) -> logging.Logger:
    """
    Set up performance logging for timing measurements.

    Parameters
    ----------
    log_file : str, optional
        Path to performance log file
    level : int, optional
        Logging level

    Returns
    -------
    logging.Logger
        Performance logger
    """
    # Create performance logger
    perf_logger = logging.getLogger('performance')
    perf_logger.setLevel(level)

    # Clear existing handlers
    for handler in perf_logger.handlers[:]:
        perf_logger.removeHandler(handler)

    # Create formatter for performance logs
    formatter = logging.Formatter('%(asctime)s - %(message)s', DEFAULT_DATE_FORMAT)

    # File handler for performance logs
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    perf_logger.addHandler(file_handler)

    return perf_logger


class TimingContext:
    """
    Context manager for timing code blocks.
    """

    def __init__(self, name: str, logger: Optional[logging.Logger] = None):
        """
        Initialize timing context.

        Parameters
        ----------
        name : str
            Name of the operation being timed
        logger : logging.Logger, optional
            Logger to use. If None, use performance logger.
        """
        self.name = name
        self.logger = logger or logging.getLogger('performance')
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"START: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        if exc_type is None:
            self.logger.info(f"END: {self.name} - {duration:.2f}s")
        else:
            self.logger.error(f"ERROR in {self.name}: {exc_val} - {duration:.2f}s")

        return False  # Don't suppress exceptions


def log_memory_usage(logger: logging.Logger, message: str = "Memory usage") -> None:
    """
    Log current memory usage.

    Parameters
    ----------
    logger : logging.Logger
        Logger instance
    message : str, optional
        Message prefix
    """
    try:
        import psutil
        import os

        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()

        # Convert to MB
        rss_mb = mem_info.rss / 1024 / 1024
        vms_mb = mem_info.vms / 1024 / 1024

        logger.debug(f"{message}: RSS={rss_mb:.1f}MB, VMS={vms_mb:.1f}MB")

    except ImportError:
        logger.debug("psutil not installed, memory logging disabled")
    except Exception as e:
        logger.debug(f"Error logging memory usage: {e}")