import os
import socket
from DatabaseManager import Database


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.database = Database("Dice-Database.db")

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

    def receive_data(self):
        try:
            packetID = self.client_socket.recv(1).decode()
            print(f"packetID {packetID}")
            data_length = self.client_socket.recv(4).decode()
            print(f"data_length {data_length}")
            if int(packetID) == 1:
                pass
        except Exception as e:
            print(f"Error receiving data: {e}")

    def send_file_to_server(self, file_path: str) -> None:
        """
        Send a file to the server.

        This method sends the file name, file size, and file data to the server.
        :param file_path: The path of the file to send.
        """
        file_name = os.path.basename(file_path)

        file = open(file_path, "rb")
        file_size = os.path.getsize(file_path)
        file_data = file.read()
        file.close()

        file_info = f"{file_name}|{file_size}"
        data = f"{2}{Client.zero_fill_length(file_info)}{file_info}".encode()
        print(f"{2}{Client.zero_fill_length(file_info)}{file_info} FILEDATA[END]]")
        self.client_socket.sendall(data)
        self.client_socket.sendall(file_data)
        self.client_socket.send(b"[END]")

    def request_signup(self, username, password):
        data = f"{username}|{password}"
        data = f"{1}{Client.zero_fill_length(data)}{data}".encode()
        self.client_socket.send(data)

        response = self.client_socket.recv(19).decode()
        if response.startswith("no"):
            return False
        else:
            self.database.create_new_account(username, password, int(response))
            return True




    @staticmethod
    def zero_fill_length(input_string, width=4):
        length = len(input_string)
        length_str = str(length).zfill(width)
        return length_str



if __name__ == "__main__":
    client = Client('LocalHost', 12345)
    client.connect_to_server()
