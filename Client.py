import os
import socket

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to the server at {self.host}:{self.port}")
        except Exception as e:
            print(f"Connection error: {str(e)}")

    def send_data(self, data, sendall=False):
        try:
            if sendall:
                self.client_socket.sendall((str(data)).encode())
            else:
                self.client_socket.send((str(data)).encode())
        except Exception as e:
            print(f"Error sending data to the server: {e}")


if __name__ == "__main__":
    client = Client('LocalHost', 12345)
    client.connect_to_server()
