import os
import tqdm
import socket

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port



    def start(self):
        # Create a server socket and listen for client connections
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        print(f"Server is listening for connections")
        client_socket, addr = server_socket.accept()
        print(f"New client connected: {client_socket.getpeername()}")


if __name__ == "__main__":
    server = Server('0.0.0.0', 12345)
    server.start()
