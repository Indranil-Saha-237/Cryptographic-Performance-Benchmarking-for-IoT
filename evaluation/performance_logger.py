# performance_logger.py
import logging
import os
from datetime import datetime


class PerformanceLogger:
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, f'performance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('HybridCryptoFramework')
        self.logger.info(f"Performance logging initialized: {log_file}")

    def log_operation(self, operation: str, details: dict):
        self.logger.info(f"{operation}: {details}")

    def log_error(self, error: str, details: dict = None):
        self.logger.error(f"{error}: {details or {}}")

    def log_summary(self, summary: dict):
        self.logger.info("="*60)
        self.logger.info("PERFORMANCE SUMMARY")
        self.logger.info("="*60)
        for key, value in summary.items():
            self.logger.info(f"{key}: {value}")
        self.logger.info("="*60)
