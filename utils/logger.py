"""
KYKSKN - Logging Utilities
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from config.settings import LOG_DIR, LOG_FORMAT, LOG_DATE_FORMAT


class Logger:
    """Centralized logging system"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.logger = None
        self.log_file = None
        
    def setup(self, session_name: str = None):
        """Setup logging system"""
        # Create log directory
        Path(LOG_DIR).mkdir(parents=True, exist_ok=True)
        
        # Generate log filename
        if session_name is None:
            session_name = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.log_file = os.path.join(LOG_DIR, f"kykskn_{session_name}.log")
        
        # Configure logger
        self.logger = logging.getLogger('KYKSKN')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        
        # Console handler (only errors)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def _safe_message(self, message):
        """Convert message to safe string format - prevents substitute error"""
        if message is None:
            return "None"
        if isinstance(message, str):
            return message
        try:
            return str(message)
        except Exception:
            return f"<unprintable object: {type(message).__name__}>"
    
    def info(self, message):
        """Log info message"""
        if self.logger:
            self.logger.info(self._safe_message(message))
    
    def warning(self, message):
        """Log warning message"""
        if self.logger:
            self.logger.warning(self._safe_message(message))
    
    def error(self, message):
        """Log error message"""
        if self.logger:
            self.logger.error(self._safe_message(message))
    
    def debug(self, message):
        """Log debug message"""
        if self.logger:
            self.logger.debug(self._safe_message(message))
    
    def critical(self, message):
        """Log critical message"""
        if self.logger:
            self.logger.critical(self._safe_message(message))


# Global logger instance
logger = Logger()

