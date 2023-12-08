import os
import socket

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to the server at {self.host}:{self.port}")
        except Exception as e:
            print(f"Connection error: {str(e)}")

    def send_data(self, data, need_encode=True, sendall=False):
        try:
            if sendall:
                self.client_socket.sendall(data)
            elif need_encode:
                self.client_socket.send((str(data)).encode())
            elif not sendall and not need_encode:
                self.client_socket.send(data)
        except Exception as e:
            print(f"Error sending data to the server: {e}")

    def send_file_to_server(self, file_name):
        file = open(file_name, "rb")
        file_size = os.path.getsize(file_name)
        file_data = file.read()

        self.send_data(file_name)
        self.send_data(file_size)
        self.send_data(file_data, sendall=True)
        self.send_data(b"[END]", need_encode=False)

        file.close()

if __name__ == "__main__":
    client = Client('LocalHost', 12345)
    client.connect_to_server()
    client.send_file_to_server("tomerXd.mp4")
