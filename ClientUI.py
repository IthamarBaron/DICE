import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import PhotoImage
from Client import Client

BACKGROUND_COLOR = "#00274C"

class ManagerUI:
    def __init__(self, root):
        self.root = root
        self.current_frame = None
        self.connect_frame()

    def connect_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.current_frame.pack(expand=True, fill=tk.BOTH)

        self.root.geometry("500x400")
        self.root.title("Connect to Server")

        # title
        large_text_label = tk.Label(self.current_frame, text="CONNECT TO SERVER", font=("Arial", 24, "bold"),
                                    bg=BACKGROUND_COLOR, fg="white")
        large_text_label.pack(pady=20)

        #  photo
        image_path = "server_connection_icon.png"
        self.image = PhotoImage(master=self.current_frame, width=200, height=100, file=image_path)

        image_label = tk.Label(self.current_frame, image=self.image, bg=BACKGROUND_COLOR)
        image_label.pack(pady=(20, 0))

        # String Input Field
        self.entry = tk.Entry(self.current_frame, font=('Arial', 14), fg="white", bg="#D3D3D3", bd=3, relief="solid",
                              insertbackground="black")
        self.entry.insert(0, "ENTER IP")
        self.entry.pack(pady=20)

        # Connect Button
        connect_button = tk.Button(self.current_frame, text="Connect", command=self.connect_to_server, bg="#4CAF50", fg="black",
                                   bd=2, relief="solid", width=15, height=2)
        connect_button.pack(pady=20)

        # labels
        label_dice = tk.Label(self.current_frame, text="DICE", font=("Rubik", 10, "bold", "underline"), fg="white",
                              bg=BACKGROUND_COLOR)
        label_description = tk.Label(self.current_frame, text="~Discord Integrated Cryptographic Engine",
                                     font=("Rubik", 9, "bold"), fg="white", bg=BACKGROUND_COLOR)
        label_description.pack(side=tk.BOTTOM, anchor=tk.W)
        label_dice.pack(side=tk.BOTTOM, anchor=tk.W)

    def connect_to_server(self):
        ip = self.entry.get()
        print(f"Attempting to connect to: {ip}")
        self.client_instance = Client(ip, 12345)
        self.client_instance.connect_to_server()

        # If connection is successful, switch to the file upload frame
        self.current_frame.destroy()
        self.file_upload_frame()

    def file_upload_frame(self):
        self.current_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.root.title("File Upload")

        # title
        self.title_label = tk.Label(self.root, text="Welcome to Dice", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # file upload button
        self.upload_button = tk.Button(self.root, text="Upload File", command=self.upload_file)
        self.upload_button.pack(pady=20)

        # send button
        self.send_button = tk.Button(self.root, text="Send", command=self.send_data)
        self.send_button.pack(pady=20)

    def upload_file(self):
        self.uploded_file_path = filedialog.askopenfilename()


    def send_data(self):
        thread = threading.Thread(target=self.client_instance.send_file_to_server, args=(self.uploded_file_path,))
        thread.start()
        pass
def main():
    root = tk.Tk()
    app_controller = ManagerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
