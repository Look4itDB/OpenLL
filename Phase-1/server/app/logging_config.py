# app/logging_config.py
import logging

def configure_logging(app):
    # Set up file-only logging (no console output)
    log_handler = logging.FileHandler("logFile.txt", mode='a')
    log_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    log_handler.setFormatter(formatter)
    
    # Remove default handlers and add our file handler
    app.logger.handlers = []
    app.logger.addHandler(log_handler)
    app.logger.setLevel(logging.INFO)
