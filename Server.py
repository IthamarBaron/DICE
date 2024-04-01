import asyncio
import json

import Protocol
from DatabaseManager import Database

import socket
import DiscordBot
import threading


class Server:

    def __init__(self, host, port, token):
        self.host = host
        self.port = port
        self.packet_handlers = [None, self.handle_sign_up_request, self.handle_file_and_send_to_discord,
                                self.handle_file_request, self.handle_deletion_request, self.handle_login_request,
                                self.handle_files_for_initiation]
        self.database = Database("Dice-Database.db")
        self.bot_instance = DiscordBot.DiscordBot(token)
        thread = threading.Thread(target=self.bot_instance.run_discord_bot, daemon=True)
        thread.start()

    def start(self) -> None:
        """
        Start server and waits for client connections.
        Creates a server socket, binds to host and port, and listens for clients.
        Upon connection, prints client information.
        :return: None
        """
        Protocol.Protocol.generate_key()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        print(f"Server is listening for connections")

        self.client_socket, _ = server_socket.accept()
        print(f"New client connected: {self.client_socket.getpeername()}")
        self.receive_data()


    def receive_data(self):
        try:
            packetID = int(self.client_socket.recv(1).decode())
            print(f"packetID {packetID}")
            data_length = int(self.client_socket.recv(4).decode())
            print(f"data_length {data_length}")
            self.packet_handlers[packetID](data_length)

        except Exception as e:
            print(f"Error receiving data: {e}")

    def receive_file(self, data_length):
        """
        Receive a file from a connected client.
        This method expects the client to send the file name, file size, and file data.
        :return: None
        """
        try:
            file_info = self.client_socket.recv(int(data_length)).decode()
            file_info = json.loads(file_info)

            file_name = file_info["file_name"]
            file_size = int(file_info["file_size"])
            channel_id = int(file_info["channel_id"])

            print(f"Receiving file: {file_name} of size: {file_size / (1024 ** 2):.2f} MB")

            file_bytes = b""
            while len(file_bytes) != file_size:
                part_of_file = self.client_socket.recv(file_size - len(file_bytes))
                if not len(part_of_file):
                    print("Connection lost")
                    return [0, 0, 0]
                file_bytes += part_of_file
            file_bytes = Protocol.Protocol.decrypt_incoming_data(file_bytes)
            return [file_name, file_bytes, channel_id]
        except Exception as e:
            print(f"Error receive file: {e}")
        return [0, 0, 0]

    def send_files_to_discord(self, file_name, file_content, channel_id):
        print(f"Sending file [{file_name}] in channel [{self.bot_instance.bot.get_channel(channel_id)}]")
        temp = asyncio.run_coroutine_threadsafe(
            self.bot_instance.send_file_in_chat(file_name, file_content, channel_id), self.bot_instance.bot.loop)
        reference_message_info = temp.result()
        if reference_message_info:
            print(f"Message sent successfully")
            self.database.new_file_in_channel(reference_message_info[0], reference_message_info[1], channel_id)

    # region Handlers

    def handle_sign_up_request(self, data_length):
        data = self.client_socket.recv(int(data_length)).decode()
        data = Protocol.Protocol.decrypt_incoming_data(data)
        data = json.loads(data)

        print(data)

        if not self.database.is_username_availability(data["username"]):
            print("Username unavailable")
            #  hahaha i am 19 chars long
            data = "noooooooooooooooooo"
            data = f"{data}"
            self.client_socket.send(data.encode())
            pass
        else:
            print("username available")
            attempt_channel_creation = asyncio.run_coroutine_threadsafe(self.bot_instance.create_new_storage_area(data["username"]),
                                                    self.bot_instance.bot.loop)
            channel_id = attempt_channel_creation.result()
            self.database.create_new_account(data["username"], data["password"], channel_id)
            print(channel_id)
            data = f"{channel_id}"
            self.client_socket.send(data.encode())

    def handle_file_and_send_to_discord(self, data_length):

        file_data = self.receive_file(data_length)  # fil name | file content | channelID
        if file_data[1]:
            self.send_files_to_discord(file_data[0], file_data[1], file_data[2])

    def handle_file_request(self, data_length):
        requested_file_info = self.client_socket.recv(int(data_length)).decode()
        requested_file_info = Protocol.Protocol.decrypt_incoming_data(requested_file_info)
        requested_file_info = json.loads(requested_file_info)  # file_name , channel_id

        message_id = self.database.get_message_id_by_name(requested_file_info["file_name"],
                                                          int(requested_file_info["channel_id"]))

        if message_id != 0:
            temp = asyncio.run_coroutine_threadsafe(
                self.bot_instance.assemble_file_from_chat(message_id, int(requested_file_info["channel_id"])),
                self.bot_instance.bot.loop)
            file_bytes = temp.result()


            packet = {
                "file_name": requested_file_info["file_name"],
                "len_file_bytes": len(file_bytes)
            }

            data = f"{2}{self.zero_fill_length(str(packet))}{json.dumps(packet)}".encode()
            self.client_socket.sendall(data)
            self.client_socket.sendall(file_bytes)
        else:
            print("message id is 0")

    def handle_deletion_request(self, data_length):
        data = self.client_socket.recv(data_length).decode()
        data = Protocol.Protocol.decrypt_incoming_data(data)
        data = json.loads(data)

        message_id = self.database.get_message_id_by_name(data["file_name"], int(data["channel_id"]))

        proc = asyncio.run_coroutine_threadsafe(self.bot_instance.delete_file_from_chat(message_id,
                                                int(data["channel_id"])), self.bot_instance.bot.loop)
        is_successful = proc.result()
        if is_successful:
            print("successful!")
            self.database.delete_file_in_table(data["file_name"], data["channel_id"])
        # TODO: make threaded

    def handle_login_request(self, data_length):
        print("================HANDLE_LOGIN_REQUEST==========")
        encrypted_packet = self.client_socket.recv(data_length)
        print(f"encrypted data = {encrypted_packet }")
        data = Protocol.Protocol.decrypt_incoming_data(encrypted_packet )
        print(f"decrypted data = {data}")
        data = json.loads(data.decode())
        print(f"loaded data = {data}")

        row = self.database.attempt_login(data["username"], data["password"])
        packet = {
            "row": row
        }
        print(row)
        data_to_send = f"{1}{self.zero_fill_length(str(packet))}{json.dumps(packet)}".encode()
        self.client_socket.sendall(data_to_send)

    def handle_files_for_initiation(self, data_length):
        data = self.client_socket.recv(data_length).decode()
        data = Protocol.Protocol.decrypt_incoming_data(data)
        data = json.loads(data)
        files = self.database.get_files_from_id(data["channel_id"])

        packet = {
            "files": files
        }
        print(f"Files: {files}")
        data_to_send = f"{3}{self.zero_fill_length(str(packet))}{json.dumps(packet)}".encode()
        self.client_socket.send(data_to_send)


    # endregion Handlers

    @staticmethod
    def zero_fill_length(input_string, width=4):
        length = len(input_string)
        length_str = str(length).zfill(width)
        return length_str


if __name__ == "__main__":
    server = Server('LocalHost', 12345, "")
    server.start()
    while True:
        server.receive_data()