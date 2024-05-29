import socket
import threading
import numpy as np
import time

HOST = "127.0.0.1"
PORT = 7500

# Function to handle client connections
def handle_client(conn, addr, logger, verbose):
    print(f"Connected by {addr}")
    try:
        while True:
            try:
                #sending data
                y_accel = np.random.randint(0, 255) + round(np.random.random(), 2)
                y_gyro = np.random.randint(0, 255) + round(np.random.random(), 2)
                y_PID = np.random.randint(0, 255) + round(np.random.random(), 2)
                time.sleep(1)

                if verbose:
                    logger.log("Server", f"Set Y values of: {y_accel}, {y_gyro}, {y_PID}")

                data = f"{y_accel},{y_gyro},{y_PID}\n"
                conn.send(data.encode())

                #getting data
                try:
                    recv_data = conn.recv(1024).decode("utf-8")
                except TimeoutError:
                    continue #timeout

                if verbose:
                    logger.log("Server", f"received data: {recv_data}")
            except ConnectionResetError:
                print("reset")
                break
                
    except ConnectionResetError and BrokenPipeError:
        conn.close()
        print(f"Connection closed by {addr}")

# Main function to start the server
def run_server(logger, verbose = False):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            conn.settimeout(1)
            client_thread = threading.Thread(target=handle_client, args=(conn, addr, logger, verbose))
            client_thread.start()

if __name__ == "__main__":
    run_server()