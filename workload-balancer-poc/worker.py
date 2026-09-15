import socket
import time

HOST = "127.0.0.1"
PORT = 3000
THROTTLE = 2

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    try:
        client_socket.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT}")

        message = 0
        while True:
            client_socket.sendall(str(message).encode("utf-8"))
            print(f"Sent: {message}")
            message += 1
            time.sleep(THROTTLE)

    except ConnectionRefusedError:
        print("Could not connect to the server. Is server.py running?")