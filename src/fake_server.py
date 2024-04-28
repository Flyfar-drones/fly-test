import socket
import numpy as np
import time

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 7500
    client_sockets = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        client_socket, addr = s.accept()
        client_sockets.append(client_socket)
        with client_socket:
            print(f"Connected by {addr}")
            while True:
                y_accel = np.random.randint(0, 255) + round(np.random.random(), 2)
                y_gyro = np.random.randint(0, 255) + round(np.random.random(), 2)
                y_PID = np.random.randint(0, 255) + round(np.random.random(), 2)
                time.sleep(1)

                print(y_accel, y_gyro, y_PID)

                data = f"{y_accel},{y_gyro},{y_PID}\n"
                for i, client in enumerate(client_sockets):
                    client.send(data.encode())