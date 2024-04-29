#
# Main testing header to monitor
#

import threading

from main import run_app
from fake_server import run_server

class Tester:
    def __init__(self):
        self.data_from_app = []
        self.data_from_server = []

    def run_tester(self):
        self.thread_app = threading.Thread(target=run_app)
        self.thread_server = threading.Thread(target=run_server)

        self.thread_app.start()
        self.thread_server.start()

        self.thread_app.join()
        self.thread_server.join

if __name__ == "__main__":
    tester = Tester()
    tester.run_tester()
