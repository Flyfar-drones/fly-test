#
# Main testing header to monitor
#

import threading
import logging
import os
import sys

from main import run_app
from fake_server import run_server

class CustomLogger:
    def __init__(self, logger_path, logger_name):
        #setup logger
        if os.path.exists(logger_path):
            os.remove(logger_path)

        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

        self.file_logger = logging.FileHandler(logger_path)
        self.file_logger.setLevel(logging.INFO)
        self.file_logger.setFormatter(logFormatter)

        self.stream_logger = logging.StreamHandler(sys.stdout)
        self.stream_logger.setLevel(logging.INFO)
        self.stream_logger.setFormatter(logFormatter)

        self.logger.addHandler(self.file_logger)
        self.logger.addHandler(self.stream_logger)

        self.log("Tester", "Logger is set up")
    
    def log(self, log_part, log_message):
        self.logger.info(f"({log_part}) {log_message}")

    def error(self, log_part, log_message):
        self.logger.error(f"({log_part}) {log_message}")

class Tester:
    def __init__(self, logger):
        self.data_from_app = []
        self.data_from_server = []
        self.logger = logger

    def run_tester(self):
        self.thread_app = threading.Thread(target=run_app, args=(self.logger, True,))
        self.thread_server = threading.Thread(target=run_server, args=(self.logger, True,))

        self.logger.log("Tester", "Started")

        self.thread_app.start()
        self.thread_server.start()

        self.thread_app.join()
        self.thread_server.join()

if __name__ == "__main__":
    logger = CustomLogger("./logs/tester.log", "tester-log")
    tester = Tester(logger)
    tester.run_tester()
