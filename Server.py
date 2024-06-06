import asyncio
import json

import Protocol
from DatabaseManager import Database

import socket
import DiscordBot
import threading


class Server:

    def __init__(self, host, port, token):
        self.server_protocol_instance = None
        self.host = host
        self.port = port
        self.clients = {}
        self.client_threads = []
        self.packet_handlers = [None, self.handle_sign_up_request, self.handle_file_and_send_to_discord,
                                self.handle_file_request, self.handle_deletion_request, self.handle_login_request,
                                self.handle_files_for_initiation]
        #self.database = Database("Dice-Database.db")
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


        Protocol.Protocol.generate_key() #TODO: SWAP LATER
        self.server_protocol_instance = Protocol.ServerProtocol()
        self.server_protocol_instance.create_server_keys()
        print(f" [MAIN THREAD] Server public key in server {self.server_protocol_instance.get_public_key()}")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        connected_clients = 0
        while True:

            server_socket.listen()
            print(f" [MAIN THREAD] Server is listening for connections")
            client_socket, _ = server_socket.accept()  # ACCEPT CONNECTION
            print(f" [MAIN THREAD] client connected: {client_socket.getpeername()}")
            self.clients[connected_clients] = [client_socket]  # Add the client to the dict

            new_client_thread = threading.Thread(target=self.run_server_for_client, args=(connected_clients,), daemon=True)
            self.client_threads.append(new_client_thread)
            new_client_thread.start()
            connected_clients += 1


    def run_server_for_client(self, client_id):
        self.clients[client_id].append(Database("Dice-Database.db"))
        packet = {
            "server_public_key": str(self.server_protocol_instance.get_public_key()),
        }
        data_to_send = f"{0}{self.zero_fill_length(str(packet))}{json.dumps(packet)}".encode()
        self.clients[client_id][0].sendall(data_to_send)
        is_connected = True
        while is_connected:
            is_connected = self.receive_data(client_id)


    def receive_data(self, client_id):
        try:
            packet_id = int(self.clients[client_id][0].recv(1).decode())
            print(f" [CLIENT_THREAD {client_id}] packet_id {packet_id}")
            data_length = int(self.clients[client_id][0].recv(4).decode())
            print(f" [CLIENT_THREAD {client_id}] data_length {data_length}")
            self.packet_handlers[packet_id](data_length, client_id)

        except ValueError:
            return True # client disconnected
        except Exception as e:
            print(f" [CLIENT_THREAD {client_id}] Error receiving data: {e}")
        finally:
            return True

    def receive_file(self, data_length, client_id):
        """
        Receive a file from a connected client.
        This method expects the client to send the file name, file size, and file data.
        :return: None
        """
        try:
            data = self.clients[client_id][0].recv(int(data_length)).decode()
            data = Protocol.Protocol.decrypt_incoming_data(data)
            file_info = json.loads(data)
            file_name = file_info["file_name"]
            file_size = int(file_info["file_size"])
            channel_id = int(file_info["channel_id"])

            print(f"Receiving file: {file_name} of size: {file_size / (1024 ** 2):.2f} MB")

            file_bytes = b""
            while len(file_bytes) != file_size:
                part_of_file = self.clients[client_id][0].recv(file_size - len(file_bytes))
                if not len(part_of_file):
                    print("Connection lost")
                    return [0, 0, 0]
                file_bytes += part_of_file
            #file_bytes = Protocol.Protocol.decrypt_incoming_data(file_bytes)
            return [file_name, file_bytes, channel_id]
        except Exception as e:
            print(f"Error receive file: {e}")
        return [0, 0, 0]

    def send_files_to_discord(self, file_name, file_content, channel_id, client_id):
        print(f" [CLIENT_THREAD {client_id}] Sending file [{file_name}] in channel [{self.bot_instance.bot.get_channel(channel_id)}]")
        temp = asyncio.run_coroutine_threadsafe(
            self.bot_instance.send_file_in_chat(file_name, file_content, channel_id), self.bot_instance.bot.loop)
        reference_message_info = temp.result()
        if reference_message_info:
            print(f" [CLIENT_THREAD {client_id}] Message sent successfully")
            self.clients[client_id][1].new_file_in_channel(reference_message_info[0], reference_message_info[1], channel_id)

    # region Handlers
    def handle_file_and_send_to_discord(self, data_length, client_id):
        file_data = self.receive_file(data_length, client_id)  # fil name | file content | channelID
        if file_data[1]:
            self.send_files_to_discord(file_data[0], file_data[1], file_data[2], client_id)

    def handle_sign_up_request(self, data_length, client_id):
        data = self.clients[client_id][0].recv(int(data_length)).decode()
        data = Protocol.Protocol.decrypt_incoming_data(data)
        data = json.loads(data)

        print(data)

        if not self.clients[client_id][1].is_username_availability(data["username"]):
            print(f" [CLIENT_THREAD {client_id}] Username unavailable")
            #  hahaha i am 19 chars long
            data = "noooooooooooooooooo"
            data = f"{data}"
            self.clients[client_id][0].send(data.encode())
            pass
        else:
            print(f" [CLIENT_THREAD {client_id}] username available")
            attempt_channel_creation = asyncio.run_coroutine_threadsafe(self.bot_instance.create_new_storage_area(data["username"]),
                                                    self.bot_instance.bot.loop)
            channel_id = attempt_channel_creation.result()
            self.clients[client_id][1].create_new_account(data["username"], data["password"], channel_id)
            print(channel_id)
            data = f"{channel_id}"
            self.clients[client_id][0].send(data.encode())



    def handle_file_request(self, data_length, client_id):
        requested_file_info = self.clients[client_id][0].recv(int(data_length)).decode()
        requested_file_info = Protocol.Protocol.decrypt_incoming_data(requested_file_info)
        requested_file_info = json.loads(requested_file_info)  # file_name , channel_id

        message_id = self.clients[client_id][1].get_message_id_by_name(requested_file_info["file_name"],
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
            self.clients[client_id][0].sendall(data)
            self.clients[client_id][0].sendall(file_bytes)
        else:
            print(f" [CLIENT_THREAD {client_id}] message id is 0")

    def handle_deletion_request(self, data_length,client_id):
        data = self.clients[client_id][0].recv(data_length).decode()
        data = Protocol.Protocol.decrypt_incoming_data(data)
        data = json.loads(data)

        message_id = self.clients[client_id][1].get_message_id_by_name(data["file_name"], int(data["channel_id"]))

        proc = asyncio.run_coroutine_threadsafe(self.bot_instance.delete_file_from_chat(message_id,
                                                int(data["channel_id"])), self.bot_instance.bot.loop)
        is_successful = proc.result()
        if is_successful:
            print(f" [CLIENT_THREAD {client_id}] successful!")
            self.clients[client_id][1].delete_file_in_table(data["file_name"], data["channel_id"])
        # TODO: make threaded

    def handle_login_request(self, data_length, client_id):
        encrypted_packet = self.clients[client_id][0].recv(data_length)
        data = Protocol.Protocol.decrypt_incoming_data(encrypted_packet )
        data = json.loads(data.decode())

        row = self.clients[client_id][1].attempt_login(data["username"], data["password"])
        packet = {
            "row": row
        }
        print(row)
        data_to_send = f"{1}{self.zero_fill_length(str(packet))}{json.dumps(packet)}".encode()
        self.clients[client_id][0].sendall(data_to_send)

    def handle_files_for_initiation(self, data_length, client_id):
        encrypted_packet = self.clients[client_id][0].recv(data_length)
        data = Protocol.Protocol.decrypt_incoming_data(encrypted_packet )
        data = json.loads(data.decode())
        files = self.clients[client_id][1].get_files_from_id(data["channel_id"])

        packet = {
            "files": files
        }
        print(f"Files: {files}")
        data_to_send = f"{3}{self.zero_fill_length(str(packet))}{json.dumps(packet)}".encode()
        self.clients[client_id][0].send(data_to_send)


    # endregion Handlers

    @staticmethod
    def zero_fill_length(input_string, width=4):
        length = len(input_string)
        length_str = str(length).zfill(width)
        return length_str


if __name__ == "__main__":
    server = Server('LocalHost', 12345, "")
    server.start()
