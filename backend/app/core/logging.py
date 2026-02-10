import os
import logging
import logging.config
from pathlib import Path

def setup_logging():
    """
    Setup logging configuration
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "meetcode.log"

    # Clear logs on startup
    with open(log_file, "w") as f:
        f.truncate(0)

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "access": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "file": {
                "formatter": "default",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(log_file),
                "mode": "a", # Append mode (since we manually cleared it)
                "maxBytes": 10485760, # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console", "file"],
                "level": "INFO",
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["file"], # Already has console
                "propagate": True,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["file"], # Already has console
                "propagate": True,
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": True,
            },
            "sqlalchemy.engine": {
                 "level": "INFO",
                 "handlers": ["file"],
                 "propagate": False, # Don't double print to console if root has it
            }
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)
