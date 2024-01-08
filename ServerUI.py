import multiprocessing
from Server import Server

class ServerUI:

    def __init__(self, token, ip='LocalHost', port=12345):
        self.server_instance = Server(ip, port, token)
        self.server_process = None

    def start_server(self):
        self.server_instance.start()
        while True:
            self.server_instance.receive_data()

    def process_start_server(self):
        self.server_process = multiprocessing.Process(target=self.start_server)
        self.server_process.daemon = True
        self.server_process.start()

    def stop_server(self):
        if self.server_process and self.server_process.is_alive():
            self.server_process.terminate()
