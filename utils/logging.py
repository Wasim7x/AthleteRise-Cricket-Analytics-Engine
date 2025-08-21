import logging
import os
from datetime import datetime

def setup_logger(log_filename="app_status.log"):
    """One-function logging setup"""
    
    os.makedirs('logs', exist_ok=True)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(f'logs/{log_filename}'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)