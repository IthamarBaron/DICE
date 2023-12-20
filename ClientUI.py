import tkinter as tk
from tkinter import filedialog
from Client import Client

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
        client_instance = Client('LocalHost', 12345)
        client_instance.connect_to_server()
        client_instance.send_file_to_server("tomerXd.mp4")

        self.root.destroy()
        self.client_ui.root.deiconify()


class ClientUI:
    def __init__(self, root):
        self.root = root
        root.title("File Upload Application")

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
        # store the path in the client

    def send_data(self):
        # send the file data to the server
        pass

    def open_server_connection(self):
        # Create a new root for the server connection window
        server_root = tk.Tk()

        # Instantiate the ServerConnectionUI class
        server_connection_ui = ServerConnectionUI(server_root, self)

        # Start the Tkinter event loop for the server connection window
        server_root.mainloop()


# Create the main Tkinter window
root = tk.Tk()

# Instantiate the ClientUI class
app = ClientUI(root)

# Start the Tkinter event loop
root.mainloop()
