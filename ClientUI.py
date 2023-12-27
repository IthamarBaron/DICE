import threading
import time
import tkinter as tk
from tkinter import filedialog
from Client import Client

client_instance = Client('LocalHost', 12345)
class ServerConnectionUI:
    def __init__(self, root, client_ui):
        self.root = root
        self.client_ui = client_ui

        root.title("Connect to Server")

        # Create and place the title label
        self.title_label = tk.Label(root, text="Connect to Server", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # Create and place the connect button
        self.connect_button = tk.Button(root, text="Connect", command=self.connect_to_server)
        self.connect_button.pack(pady=20)

    def connect_to_server(self):
        client_instance.connect_to_server()

        self.root.destroy()
        self.client_ui.root.deiconify()


class ClientUI:
    def __init__(self, root):
        self.root = root
        root.title("File Upload")

        # Create and place the title label
        self.title_label = tk.Label(root, text="Welcome to Dice", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # Create and place the file upload button
        self.upload_button = tk.Button(root, text="Upload File", command=self.upload_file)
        self.upload_button.pack(pady=20)

        # Create and place the send button
        self.send_button = tk.Button(root, text="Send", command=self.send_data)
        self.send_button.pack(pady=20)

        # Initially hide the client UI
        self.root.withdraw()

        # Open the server connection window
        self.open_server_connection()

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        self.uploaded_file_path = file_path
        print(f"file Path: {file_path}")


    def send_data(self):
        start_time = time.time()
        thread = threading.Thread(target=client_instance.send_file_to_server, args=(self.uploaded_file_path,))
        thread.start()
        elapsed_time = time.time() - start_time
        print(f"Time elapsed in sed_data: {elapsed_time}")


    def open_server_connection(self):
        server_root = tk.Tk()
        server_connection_ui = ServerConnectionUI(server_root, self)
        server_root.mainloop()

root = tk.Tk()
app = ClientUI(root)
root.mainloop()
