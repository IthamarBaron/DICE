import asyncio
from DatabaseManager import Database

import tqdm
import socket
import warnings
import DiscordBot
import threading

class Server:

    def __init__(self, host, port, token):
        self.host = host
        self.port = port
        self.database = Database("Dice-Database.db")
        self.bot_instance = DiscordBot.DiscordBot(token)
        thread = threading.Thread(target=self.bot_instance.run_discord_bot)
        thread.start()

    def start(self) -> None:
        """
        Start server and waits for client connections.

        Creates a server socket, binds to host and port, and listens for clients.
        Upon connection, prints client information.

        :return: None
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        print(f"Server is listening for connections")

        self.client_socket, _ = server_socket.accept()
        print(f"New client connected: {self.client_socket.getpeername()}")

    def receive_data(self):
        try:
            packetID = self.client_socket.recv(1).decode()
            print(f"packetID {packetID}")
            data_length = self.client_socket.recv(4).decode()
            print(f"data_length {data_length}")
            if int(packetID) == 1:
                self.handle_sign_up_request(data_length)
            elif int(packetID) == 2:
                self.handle_file_and_send_to_discord(data_length)
            elif int(packetID) == 3:
                self.handle_file_request(data_length)
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
            file_info = file_info.split("|")

            file_name = file_info[0]
            file_size = int(file_info[1])
            channel_id = int(file_info[2])

            print(f"Receiving file: {file_name} of size: {file_size / (1024 ** 2):.2f} MB")

            warnings.simplefilter("ignore", tqdm.TqdmWarning)
            progress = tqdm.tqdm(unit="MB", unit_scale=True, unit_divisor=1024, total=file_size/(1024 ** 2), position=0)

            file_bytes = b""
            done_receiving = False
            while not done_receiving:
                if file_bytes[-5:] == b'[END]':
                    done_receiving = True
                else:
                    part_of_file = self.client_socket.recv(1024)
                    file_bytes += part_of_file

                progress.update(1024 / (1024 ** 2))
            return [file_name, file_bytes, channel_id]
        except Exception as e:
            print(f"Error receive file: {e}")
        return [0, 0]

    def send_files_to_discord(self,file_name, file_content, channel_id):

        print(f"Sending file [{file_name}] in channel [{self.bot_instance.bot.get_channel(channel_id)}]")
        temp = asyncio.run_coroutine_threadsafe(self.bot_instance.send_file_in_chat(file_name, file_content, channel_id), self.bot_instance.bot.loop)
        reference_message_info = temp.result()
        if reference_message_info:
            print(f"Message sent successfully")
            self.database.new_file_in_channel(reference_message_info[0], reference_message_info[1], channel_id)

    def handle_file_request(self, data_length):
        requested_file_info = self.client_socket.recv(int(data_length)).decode()
        requested_file_info = requested_file_info.split("|") #filename , channel_id

        message_id = self.database.get_message_id_by_name(requested_file_info[0], int(requested_file_info[1]))
        if message_id !=0:
            temp = asyncio.run_coroutine_threadsafe(
                self.bot_instance.assemble_file_from_chat(message_id, int(requested_file_info[1])), self.bot_instance.bot.loop)
            file_bytes = temp.result()
            print(file_bytes)
        else:
            print("message id is 0")


    def handle_file_and_send_to_discord(self,data_length):

        file_data = self.receive_file(data_length)  # fil name | file content | channelID
        if file_data[1]:
            self.send_files_to_discord(file_data[0], file_data[1], file_data[2])

    def handle_sign_up_request(self,data_length):
        data = self.client_socket.recv(int(data_length)).decode()
        signup_data = data.split("|")

        if not self.database.is_username_availability(signup_data[0]):
            print("Username unavailable")
            data = "noooooooooooooooooo" #  hahaha i am 19 chars long
            data = f"{data}"
            self.client_socket.send(data.encode())
            pass
        else:
            print("username available")
            temp = asyncio.run_coroutine_threadsafe(self.bot_instance.create_new_storage_area(signup_data[0]), self.bot_instance.bot.loop)
            channel_id = temp.result()
            print(channel_id)
            data = f"{channel_id}"
            self.client_socket.send(data.encode())

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
