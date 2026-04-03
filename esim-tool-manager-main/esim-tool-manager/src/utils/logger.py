import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# Initialize colorama for Windows
try:
    import colorama
    colorama.init()
except ImportError:
    pass

_loggers = {}
_main_logger = None


def setup_logger(log_level: str = "INFO", log_dir: Optional[Path] = None) -> logging.Logger:
    """Set up the main application logger."""
    global _main_logger
    
    # Determine log directory
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log file with timestamp
    log_file = log_dir / f"tool_manager_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Create logger
    logger = logging.getLogger("esim_tool_manager")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Custom formatter with colors for Windows
    class ColorFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': '\033[36m',     # Cyan
            'INFO': '\033[32m',      # Green
            'WARNING': '\033[33m',   # Yellow
            'ERROR': '\033[31m',     # Red
            'CRITICAL': '\033[35m',  # Magenta
            'RESET': '\033[0m'       # Reset
        }
        
        def format(self, record):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            reset = self.COLORS['RESET']
            record.levelname = f"{color}{record.levelname}{reset}"
            return super().format(record)
    
    console_format = ColorFormatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_format)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    _main_logger = logger
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    global _main_logger
    
    if _main_logger is None:
        setup_logger()
    
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(f"esim_tool_manager.{name}")
    _loggers[name] = logger
    
    return logger