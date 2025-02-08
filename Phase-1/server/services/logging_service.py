import sys
sys.dont_write_bytecode = True

import logging
import os
from flask import request

# Define the path to the log file inside the 'services/' directory
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "logFile.txt")

def configure_logging(app):
    log_handler = logging.FileHandler(LOG_FILE_PATH, mode='a')
    log_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    log_handler.setFormatter(formatter)
    app.logger.handlers = []
    app.logger.addHandler(log_handler)
    app.logger.setLevel(logging.INFO)
    
    @app.after_request
    def log_request(response):
        req_data = request.get_json(silent=True)
        msg = f"{request.remote_addr} - {request.method} {request.path} - RequestData: {req_data} - ResponseCode: {response.status_code}"
        app.logger.info(msg)
        return response
