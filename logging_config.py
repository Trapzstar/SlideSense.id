# logging_config.py
import logging
import os

def setup_logging():
    log_file = os.path.join(os.path.dirname(__file__), 'voice_control.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)