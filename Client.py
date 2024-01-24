import os
import json
import time
import socket
from DatabaseManager import Database


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.database = Database("Dice-Database.db")
        self.temp_start_time = None
        self.temp_end_time = None

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
            print("receive data called!")
            packetID = self.client_socket.recv(1).decode()
            print(f"packetID {packetID}")
            data_length = self.client_socket.recv(4).decode()
            print(f"data_length {data_length}")
            if int(packetID) == 1:
                pass
            if int(packetID) ==2:
                self.get_files_from_server(data_length)
        except Exception as e:
            print(f"Error receiving data: {e}")

    def get_files_from_server(self, data_length):
        try:
            file_info = self.client_socket.recv(int(data_length)).decode()
            file_info = file_info.split("|")

            file_name = file_info[0]
            file_size = int(file_info[1])
            print(f"Receiving file: {file_name} of size: {file_size / (1024 ** 2):.2f} MB")

            received_bytes_count = 0
            file = open(f"received_{file_name}",'wb')
            while received_bytes_count != file_size:
                part_of_file = self.client_socket.recv(file_size - received_bytes_count)
                if not len(part_of_file):
                    print("Connection lost")
                    #TODO: do something about this
                file.write(part_of_file)
                received_bytes_count += len(part_of_file)
            file.close()

            self.temp_end_time = time.time()
            delta_time = int(self.temp_end_time - self.temp_start_time)
            print(f"time time elapsed: {delta_time}")
            print(f"Download average speed: {(file_size / (1024 ** 2))/delta_time}")
        except Exception as e:
            print(f"Error receive file: {e}")

    def send_file_to_server(self, file_path: str, channel_id: int) -> None:
        """
        Send a file to the server.

        This method sends the file name, file size, and file data to the server.
        :param file_path: The path of the file to send.
        :param channel_id: channel that the message will be stored in
        """
        file_name = os.path.basename(file_path)

        file = open(file_path, "rb")
        file_size = os.path.getsize(file_path)
        file_data = file.read()
        file.close()

        file_info = f"{file_name}|{file_size}|{channel_id}"
        data = f"{2}{Client.zero_fill_length(file_info)}{file_info}".encode()
        print(f"{2}{Client.zero_fill_length(file_info)}{file_info} FILEDATA")
        self.client_socket.sendall(data)
        self.client_socket.sendall(file_data)

    def request_signup(self, username, password):

        packet = {
            "packetID": 1,
            "data": {
                "username": username,
                "password": password
            }
        }
        data_to_send = f"{Client.zero_fill_length(str(packet))}{json.dumps(packet)}".encode()
        self.client_socket.send(data_to_send)

        response = self.client_socket.recv(1)
        if response == 0:
            return False
        else:
            return True

    def request_file_deletion(self, filename, channel_id):
        print("method called")
        data = f"{filename}|{channel_id}"
        data = f"{4}{self.zero_fill_length(data)}{data}"
        self.client_socket.send(data.encode())
        print("Sent file request")

    def request_download_file(self, filename, channel_id):
        self.temp_start_time = time.time()
        data = f"{filename}|{channel_id}"
        data = f"{3}{self.zero_fill_length(data)}{data}"
        self.client_socket.send(data.encode())
        self.receive_data()



    @staticmethod
    def zero_fill_length(input_string, width=10):
        length = len(input_string)
        length_str = str(length).zfill(width)
        return length_str



if __name__ == "__main__":
    client = Client('LocalHost', 12345)
    client.connect_to_server()
