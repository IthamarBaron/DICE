import warnings

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

        self.client_socket, _ = server_socket.accept()
        print(f"New client connected: {self.client_socket.getpeername()}")

    def receive_data(self, bytes_to_read):
        try:
            return self.client_socket.recv(bytes_to_read).decode()
        except Exception as e:
            print(f"Error receiving data: {e}")

    def receive_file(self):
        try:
            file_name = self.receive_data(1024)
            file_size = int(self.receive_data(1024))
            print(f"Receiving file: {file_name} of size: {file_size / (1024 ** 2):.2f} MB")

            warnings.simplefilter("ignore", tqdm.TqdmWarning)
            progress = tqdm.tqdm(unit="MB", unit_scale=True, unit_divisor=1024, total=file_size / (1024 ** 2), position=0)

            file = open(("new_" + file_name), "wb")
            file_bytes = b""
            done_receiving = False

            while not done_receiving:
                part_of_file = self.client_socket.recv(1024)
                if file_bytes[-5:] == b'[END]':
                    done_receiving = True
                else:
                    file_bytes += part_of_file
                progress.update(1024 / (1024 ** 2))

            file.write(file_bytes)
            file.close()
        except Exception as e:
            print(f"Error receive file: {e}")


if __name__ == "__main__":
    server = Server('0.0.0.0', 12345)
    server.start()
    server.receive_file()
