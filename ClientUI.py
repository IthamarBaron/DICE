import threading
import time
import tkinter as tk
from tkinter import filedialog
from Client import Client
from tkinter import PhotoImage

BACKGROUND_COLOR = "#00274C"
client_instance = Client('LocalHost', 12345)
class ServerConnectionUI:
    def __init__(self, root: tk.Tk, client_ui):
        self.root = root
        self.root.geometry("500x400")
        self.root.title("Connect to Server")

        self.root = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.root.pack(expand=True, fill=tk.BOTH)

        # Large Text Label
        large_text_label = tk.Label(self.root, text="CONNECT TO SERVER", font=("Arial", 24, "bold"), bg=BACKGROUND_COLOR, fg="white")
        large_text_label.pack(pady=20)

        # Load your image
        image_path = "server_connection_icon.png"  # Replace with the actual path to your image
        self.image = PhotoImage(master = self.root, width=200, height=100, file=image_path)

        image_label = tk.Label(self.root, image=self.image, bg=BACKGROUND_COLOR)
        image_label.pack(pady=(20, 0))

        # String Input Field
        self.entry = tk.Entry(self.root, font=('Arial', 14), fg="white", bg="#D3D3D3", bd=3, relief="solid", insertbackground="black")
        self.entry.insert(0, "ENTER IP")
        self.entry.pack(pady=20)

        # Connect Button
        connect_button = tk.Button(self.root, text="Connect", command=self.connect_to_server, bg="#4CAF50", fg="black", bd=2, relief="solid", width=15, height=2)
        connect_button.pack(pady=20)

        # labels
        label_dice = tk.Label(self.root, text="DICE", font=("Rubik", 10,"bold","underline"), fg="white", bg=BACKGROUND_COLOR)
        label_description = tk.Label(self.root, text="~Discord Integrated Cryptographic Engine",font=("Rubik", 9,"bold"), fg="white", bg=BACKGROUND_COLOR)
        label_description.pack(side=tk.BOTTOM, anchor=tk.W)
        label_dice.pack(side=tk.BOTTOM, anchor=tk.W)

    def get_ip(self):
        ip = self.entry.get()
        print(ip)

    def connect_to_server(self):
        ip = self.entry.get()
        print(ip)
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
