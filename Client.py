import base64
import os
import json
import time
import socket

import Protocol


class Client:
    def __init__(self, host, port):
        self.symmetric_key = None
        self.symmetric_protocol_instance = Protocol.SymmetricEncryptionProtocol()
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
            Protocol.Protocol.load_key()
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
            encrypted_packet = self.client_socket.recv(data_length)
            data = self.symmetric_protocol_instance.decrypt_packet(self.symmetric_key, encrypted_packet)
            file_info = json.loads(data)

            file_name = file_info["file_name"]
            file_size = int(file_info["len_file_bytes"])
            print(f"Receiving file: {file_name} of size: {file_size / (1024 ** 2):.2f} MB")

            received_bytes_count = 0
            file = open(f"received_{file_name}", 'wb')
            while received_bytes_count < file_size:
                part_of_file = self.client_socket.recv(min(file_size - received_bytes_count, 4096))
                if not part_of_file:
                    print("Connection lost")
                    break
                file.write(part_of_file)
                received_bytes_count += len(part_of_file)

            file.close()
            self.temp_end_time = time.time()
            delta_time = int(self.temp_end_time - self.temp_start_time)
            print(f"Time elapsed: {delta_time} seconds")
            print(f"Download average speed: {(file_size / (1024 ** 2)) / delta_time} MB/s")
        except Exception as e:
            print(f"Error receiving file: {e}")

    def send_file_to_server(self, file_path: str, channel_id: int) -> None:
        """
        Send a file to the server.

        This method sends the file name, file size, and file data to the server
        :param file_path: The path of the file to send
        :param channel_id: channel that the message will be stored in
        """
        try:
            file_name = os.path.basename(file_path)

            with open(file_path, "rb") as file:
                file_data = file.read()
            file_size = len(file_data)

            packet = {
                "file_name": file_name,
                "file_size": file_size,
                "channel_id": channel_id
            }

            packet = json.dumps(packet)
            encrypted_packet = self.symmetric_protocol_instance.encrypt_packet(self.symmetric_key, packet)

            data_to_send = f"{2}{len(encrypted_packet):04}".encode() + encrypted_packet
            print(f"[DEBUG LOG] data_to_send header: {data_to_send[:5]}")
            print(f"[DEBUG LOG] Encrypted packet length: {len(encrypted_packet)}")
            print(f"[DEBUG LOG] Encrypted packet: {encrypted_packet}")
            print(f"[DEBUG LOG] File data: {file_data}")

            # Send header + encrypted packet
            self.client_socket.sendall(data_to_send)

            # Send file data
            self.client_socket.sendall(file_data)
            self.reload_files_flag = True
        except Exception as e:
            print(f"Error sending file: {e}")

    def request_signup(self, username, password):

        packet = {
            "username": username,
            "password": password
        }
        #data_to_send = Protocol.Protocol.prepare_data_to_send(1, packet)
        packet = json.dumps(packet)
        packet = self.symmetric_protocol_instance.encrypt_packet(self.symmetric_key,packet)
        data_to_send = f"{1}{Client.zero_fill_length(str(packet))}".encode() + packet
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
        packet = json.dumps(packet)
        packet = self.symmetric_protocol_instance.encrypt_packet(self.symmetric_key, packet)
        data_to_send = f"{4}{Client.zero_fill_length(str(packet))}".encode() +packet
        self.client_socket.send(data_to_send)
        self.reload_files_flag = True
        print("Sent deletion request")

    def request_download_file(self, file_name, channel_id):
        self.temp_start_time = time.time()

        packet = {
            "file_name": file_name,
            "channel_id": channel_id
        }
        #data_to_send = Protocol.Protocol.prepare_data_to_send(3,packet)
        packet = json.dumps(packet)
        packet = self.symmetric_protocol_instance.encrypt_packet(self.symmetric_key, packet)

        data_to_send = f"{3}{Client.zero_fill_length(str(packet))}".encode()
        data_to_send = data_to_send+packet
        self.client_socket.send(data_to_send)
        self.receive_data()
        self.reload_files_flag = True

    def request_login(self, username, password):

        packet = {
            "username": username,
            "password": password,
        }

        #data_to_send = Protocol.Protocol.prepare_data_to_send(5, packet)
        packet = json.dumps(packet)
        packet = self.symmetric_protocol_instance.encrypt_packet(self.symmetric_key,packet)
        data_to_send = f"{5}{Client.zero_fill_length(str(packet))}".encode() + packet
        self.client_socket.send(data_to_send)
        self.receive_data()

    def request_user_files(self):

        packet = {
            "channel_id": self.user_data[2]
        }

        packet = json.dumps(packet)
        packet = self.symmetric_protocol_instance.encrypt_packet(self.symmetric_key,packet)
        #data_to_send = Protocol.Protocol.prepare_data_to_send(6,packet)
        data_to_send = f"{6}{self.zero_fill_length(str(packet))}".encode() + packet
        self.client_socket.send(data_to_send)
        self.receive_data()

    def handle_files_for_initiation(self, data_length):
        encrypted_packet = self.client_socket.recv(data_length)
        data = self.symmetric_protocol_instance.decrypt_data(self.symmetric_key, encrypted_packet)
        data = json.loads(data.decode())
        self.users_files = data["files"]
        self.reload_files_flag = True


    def handle_login_data(self, data_length):
        encrypted_packet = self.client_socket.recv(data_length)
        data = self.symmetric_protocol_instance.decrypt_data(self.symmetric_key,encrypted_packet)
        data = json.loads(data.decode())
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
        print(f"type of shit {type(self.server_publc_key)}")
        encrypted_symmetric_key = self.asymmetric_protocol_instance.encrypt_symmetric_key(self.symmetric_key, self.server_publc_key)
        encrypted_symmetric_key_base64 = base64.b64encode(encrypted_symmetric_key).decode('utf-8')

        #TODO: SEND THE SYMMETRIC KEY

        packet = {
            "encrypted_symmetric_key_base64": encrypted_symmetric_key_base64,
        }
        #data_to_send = Protocol.Protocol.prepare_data_to_send(0, packet)
        packet = json.dumps(packet)

        data_to_send = f"{0}{self.zero_fill_length(str(packet))}".encode() + packet.encode()

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