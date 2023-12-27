import os
import socket
import time


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect_to_server(self) -> None:
        """
        Connect to the server at the specified host and port.

        This method creates a client socket, connects it to the server, and prints a success
        message upon successful connection.

        :return: None
        """

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to the server at {self.host}:{self.port}")
        except Exception as e:
            print(f"Connection error: {str(e)}")

    def send_data(self, data, need_encode=True, sendall=False) -> None:
        """
        Send data to the connected server.

        This method sends the specified data to the server through the client socket.

        :param data: The data to be sent.
        :param need_encode: Flag indicating whether the data should be encoded (default is True).
        :param sendall: Flag indicating whether to use sendall method for sending all data at once (default is False).
        """
        try:
            if sendall:
                self.client_socket.sendall(data)
            elif need_encode:
                self.client_socket.send((str(data)).encode())
            elif not sendall and not need_encode:
                self.client_socket.send(data)
        except Exception as e:
            print(f"Error sending data to the server: {e}")

    def send_file_to_server(self, file_path: str) -> None:
        """
        Send a file to the server.

        This method sends the file name, file size, and file data to the server.
        :param file_path: The path of the file to send.
        """
        start_time = time.time()
        file_name = os.path.basename(file_path)

        file = open(file_path, "rb")
        file_size = os.path.getsize(file_path)
        file_data = file.read()
        file.close()

        self.send_data(file_name)
        self.send_data(file_size)
        self.send_data(file_data, sendall=True)
        self.send_data(b"[END]", need_encode=False)
        elapsed_time = time.time() - start_time
        print(f"Time elapsed in send_file_to_server : {elapsed_time}")


if __name__ == "__main__":
    client = Client('LocalHost', 12345)
    client.connect_to_server()
    client.send_file_to_server("VTOL.jpg")
