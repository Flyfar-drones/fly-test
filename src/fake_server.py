#
# Fake server for app testing
#

import socket
import numpy as np
import time

HOST = "127.0.0.1"
PORT = 7500
#client_sockets = []

def run_server(logger, verbose = False):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        client_socket, addr = s.accept()
        client_socket.settimeout(1)
        #client_sockets.append(client_socket) TODO
        client_socket
        with client_socket:
            print(f"Connected by {addr}")
            while True:
                y_accel = np.random.randint(0, 255) + round(np.random.random(), 2)
                y_gyro = np.random.randint(0, 255) + round(np.random.random(), 2)
                y_PID = np.random.randint(0, 255) + round(np.random.random(), 2)
                time.sleep(1)

                if verbose:
                    logger.log("Server", f"Set Y values of: {y_accel}, {y_gyro}, {y_PID}")

                data = f"{y_accel},{y_gyro},{y_PID}\n"
                client_socket.send(data.encode())

                try:
                    recv_data = client_socket.recv(1024).decode("utf-8")
                except TimeoutError:
                    continue #timeout

                if verbose:
                    logger.log("Server", f"received data: {recv_data}")

if __name__ == "__main__":
    run_server()