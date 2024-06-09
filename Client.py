import base64
import os
import json
import time
import socket
import Protocol


class Client:
    def __init__(self, host, port):
        self.aes = None
        self.symmetric_key = None
        self.asymmetric_protocol_instance = Protocol.AsymmetricEncryptionProtocol()
        self.host = host
        self.port = port
        self.temp_start_time = None
        self.temp_end_time = None
        self.user_data = None
        self.users_files = {}
        self.reload_files_flag = False
        self.packet_handlers = [self.handle_server_key, self.handle_login_data, self.get_file_from_server,
                                self.handle_files_for_initiation]

    def connect_to_server(self) -> bool:
        """
        Connect to the server at the specified host and port.

        This method creates a client socket, connects it to the server, and prints a success
        message upon successful connection.

        :return: Bool
        """

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to the server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False

    def receive_data(self):
        try:
            print("receive data called!")
            packet_id = int(self.client_socket.recv(1).decode())
            print(f"packetID {packet_id}")
            data_length = int(self.client_socket.recv(4).decode())
            print(f"data_length {data_length}")
            print(f"calling {str(self.packet_handlers[packet_id])}")
            self.packet_handlers[packet_id](data_length)

        except ValueError as e:
            # added this part to avoid a small error blocking new attempts
            print(f"ValueError - {e}. trying to clean the socket")
            self.client_socket.recv(1240)
        except Exception as e:
            print(f"Error receiving data: {e}")
            raise e

    def get_file_from_server(self, data_length):
        try:
            file_info = self.client_socket.recv(int(data_length)).decode()
            file_info = json.loads(file_info)

            file_name = file_info["file_name"]
            file_size = int(file_info["len_file_bytes"])
            print(f"Receiving file: {file_name} of size: {file_size / (1024 ** 2):.2f} MB")

            received_bytes_count = 0
            file = open(f"received_{file_name}", 'wb')
            while received_bytes_count != file_size:
                part_of_file = self.client_socket.recv(file_size - received_bytes_count)
                if not len(part_of_file):
                    print("Connection lost")
                    # TODO: do something about this (make faster)
                file.write(part_of_file)
                received_bytes_count += len(part_of_file)
            file.close()
            self.temp_end_time = time.time()
            delta_time = int(self.temp_end_time - self.temp_start_time)
            print(f"time time elapsed: {delta_time}")
            print(f"Download average speed: {(file_size / (1024 ** 2)) / delta_time}")
        except Exception as e:
            print(f"Error receive file: {e}")

    def send_file_to_server(self, file_path: str, channel_id: int) -> None:
        """
        Send a file to the server.

        This method sends the file name, file size, and file data to the server
        :param file_path: The path of the file to send
        :param channel_id: channel that the message will be stored in
        """
        file_name = os.path.basename(file_path)

        file = open(file_path, "rb")
        file_size = os.path.getsize(file_path)
        file_data = file.read()
        file.close()

        packet = {
            "file_name": file_name,
            "file_size": file_size,
            "channel_id": channel_id
        }

        print(f"FILEDATA {packet}")
        # file_info = Protocol.Protocol.prepare_file_info_to_send(packet, packet_id=2)
        data_to_send = f"{2}{Client.zero_fill_length(str(packet))}{Protocol.SymmetricEncryptionProtocol.encrypt_packet(self.symmetric_key, json.dumps(packet))}".encode()
        print(f"Sending packet {data_to_send}")

        self.client_socket.send(data_to_send)
        self.client_socket.sendall(file_data)
        self.reload_files_flag = True

    def request_signup(self, username, password):

        packet = {
            "username": username,
            "password": password
        }
        #data_to_send = Protocol.Protocol.prepare_data_to_send(1, packet)
        data_to_send = f"{1}{Client.zero_fill_length(str(packet))}{Protocol.SymmetricEncryptionProtocol.encrypt_packet(self.symmetric_key, json.dumps(packet))}".encode()
        print(f"Sending packet {data_to_send}")

        self.client_socket.send(data_to_send)

        response = self.client_socket.recv(19)
        print(response)
        if response == 0:
            return False
        else:
            return True

    def request_file_deletion(self, file_name, channel_id):
        packet = {
            "file_name": file_name,
            "channel_id": channel_id
        }
        print("method called")

        #data_to_send = Protocol.Protocol.prepare_data_to_send(4, packet)
        data_to_send = f"{4}{Client.zero_fill_length(str(packet))}{Protocol.SymmetricEncryptionProtocol.encrypt_packet(self.symmetric_key, json.dumps(packet))}".encode()
        print(f"Sending packet {data_to_send}")

        self.client_socket.send(data_to_send)
        self.reload_files_flag = True
        print("Sent file request")

    def request_download_file(self, file_name, channel_id):
        """
        Request to download a file from the server.

        :param file_name: The name of the file to download.
        :param channel_id: The ID of the channel where the file is located.
        :return: None
        """

        self.temp_start_time = time.time()

        packet = {
            "file_name": file_name,
            "channel_id": channel_id
        }

        encrypted_packet = Protocol.SymmetricEncryptionProtocol.encrypt_packet(self.symmetric_key, json.dumps(packet))
        data_to_send = f"{3}{Client.zero_fill_length(str(encrypted_packet))}".encode()
        data_to_send = data_to_send + encrypted_packet

        print(f"Sending packet {data_to_send}")
        self.client_socket.send(data_to_send)
        self.receive_data()
        self.reload_files_flag = True

    def request_login(self, username, password):

        packet = {
            "username": username,
            "password": password,
        }

        #data_to_send = Protocol.Protocol.prepare_data_to_send(5, packet)
        data_to_send = f"{5}{Client.zero_fill_length(self.aes.encrypt(json.dumps(packet)))}".encode() + self.aes.encrypt(json.dumps(packet))
        print(f"Sending packet {data_to_send}")

        self.client_socket.send(data_to_send)
        self.receive_data()

    def request_user_files(self):

        packet = {
            "channel_id": self.user_data[2]
        }

        #data_to_send = Protocol.Protocol.prepare_data_to_send(6,packet)
        data_to_send = f"{6}{self.zero_fill_length(str(packet))}{Protocol.SymmetricEncryptionProtocol.encrypt_packet(self.symmetric_key, json.dumps(packet))}".encode()
        print(f"Sending packet {data_to_send}")

        self.client_socket.send(data_to_send)
        self.receive_data()

    def handle_files_for_initiation(self, data_length):
        data = self.client_socket.recv(data_length).decode()
        data = json.loads(data)
        self.users_files = data["files"]
        self.reload_files_flag = True


    def handle_login_data(self, data_length):
        data = self.client_socket.recv(data_length).decode()
        data = json.loads(data)
        print(data["row"])
        self.user_data = data["row"]

    def handle_server_key(self, data_length):
        data = self.client_socket.recv(data_length).decode()
        data = json.loads(data)
        self.server_publc_key = self.asymmetric_protocol_instance.load_public_key_from_str(data["server_public_key"])
        print(f"Server public key in client {self.server_publc_key}")
        # Generate a symmetric key:
        if not self.symmetric_key:
            self.symmetric_key = Protocol.get_random_bytes(16)
            self.aes = Protocol.AESCipher(self.symmetric_key)
        print(f"symmetric key [client] {self.symmetric_key}")
        encrypted_symmetric_key = self.asymmetric_protocol_instance.encrypt_symmetric_key(self.symmetric_key, self.server_publc_key)
        encrypted_symmetric_key_base64 = base64.b64encode(encrypted_symmetric_key).decode('utf-8')

        #TODO: SEND THE SYMMETRIC KEY

        packet = {
            "encrypted_symmetric_key_base64": encrypted_symmetric_key_base64,
        }
        data_to_send = f"{0}{self.zero_fill_length(str(packet))}{json.dumps(packet)}".encode()
        print(f"Sending packet {data_to_send}")

        self.client_socket.sendall(data_to_send)


    @staticmethod
    def zero_fill_length(input_string, width=4):
        length = len(input_string)
        length_str = str(length).zfill(width)
        return length_str


"""if __name__ == "__main__":
    client = Client('LocalHost', 12345)
    client.connect_to_server()
    while True:
        client.receive_data()"""