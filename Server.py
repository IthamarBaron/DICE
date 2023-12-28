import asyncio

import tqdm
import socket
import warnings
import DiscordBot
import threading

class Server:
    def __init__(self, host, port, token):
        self.host = host
        self.port = port
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

    def receive_data(self, bytes_to_read: int) -> str:
        """
        Receive and decode data from a client.

        Attempts to receive the specified number of bytes from the client socket
        and decodes the received data into a string.
        :param: bytes_to_read: The number of bytes to receive.

        :return: The decoded string data received from the client.
        """
        try:
            return self.client_socket.recv(bytes_to_read).decode()
        except Exception as e:
            print(f"Error receiving data: {e}")

    def receive_file(self):
        """
        Receive a file from a connected client.

        This method expects the client to send the file name, file size, and file data.

        :return: None
        """
        try:
            file_name = self.receive_data(1024)
            file_size = int(self.receive_data(1024))
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
            return [file_name,file_bytes]
        except Exception as e:
            print(f"Error receive file: {e}")
        return [0, 0]

    def send_files_to_discord(self,file_name, file_content, client_id=1182998507460771890):

        #  TODO: when connecting to database assign a a channel ID to the client_id
        channel_id = client_id
        print(f"Sending file [{file_name}] in channel [{self.bot_instance.bot.get_channel(channel_id)}]")
        temp = asyncio.run_coroutine_threadsafe(self.bot_instance.send_file_in_chat(file_name, file_content, channel_id), self.bot_instance.bot.loop)
        temp.result()

    def receive_and_send_to_discord(self):
        file_data = self.receive_file()  # fil name | file content
        self.send_files_to_discord(file_data[0], file_data[1])


if __name__ == "__main__":
    server = Server('LocalHost', 12345,"MTE4Mjk5MTE2MTg3NTQ5NzAyMQ.GoCPam.3mR8XEhluS_g71W8ap0ssjMysc3dvYZOdvREZs")
    server.start()
    server.receive_and_send_to_discord()
