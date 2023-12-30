import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import PhotoImage
from Client import Client
from tkinter import font


BACKGROUND_COLOR = "#5f8ac2"

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
        image_path = "images/server_connection_icon.png"
        self.image = PhotoImage(master=self.current_frame, width=200, height=100, file=image_path)

        image_label = tk.Label(self.current_frame, image=self.image, bg=BACKGROUND_COLOR)
        image_label.pack(pady=(20, 0))

        # String Input Field
        self.entry = tk.Entry(self.current_frame, font=('Arial', 14), fg="white", bg="#D3D3D3", bd=3, relief="solid",
                              insertbackground="black")
        self.entry.insert(0, "127.0.0.1")
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
        self.login_frame()

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

    def login_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.current_frame.pack(expand=True, fill=tk.BOTH)
        self.root.geometry("500x400")

        # Title
        title_label = tk.Label(self.current_frame, text="LOG IN", font=("Rubik",25,"bold"), bg=BACKGROUND_COLOR, fg="white")
        title_label.pack(side=tk.TOP, pady=20)

        # Username Section
        username_label = tk.Label(self.current_frame, text="Name", font=("Arial", 12, "bold"), bg=BACKGROUND_COLOR, fg="black")
        username_label.pack(side=tk.TOP, padx=20, pady=(0, 0))

        username_entry = tk.Entry(self.current_frame, bg="#D3D3D3", fg="#1f1f1f", bd=2, insertbackground="black", width=45
                                  , relief=tk.SOLID,)
        username_entry.insert(0, "Enter username")
        username_entry.pack(side=tk.TOP, padx=20, pady=(0, 10), ipady=5)


        # Password Section
        password_label = tk.Label(self.current_frame, text="Password", font=("Arial", 12, "bold"), bg=BACKGROUND_COLOR,
                                  fg="black")
        password_label.pack(side=tk.TOP, padx=20, pady=(0, 0))

        password_entry = tk.Entry(self.current_frame, show="*", bg="#D3D3D3", fg="#1f1f1f", bd=2, insertbackground="black",
                                  width=45, relief=tk.SOLID)
        password_entry.pack(side=tk.TOP, padx=20, pady=(0, 10), ipady=5)

        # Buttons
        signup_button = tk.Button(self.current_frame, text="Sign Up", bg="#14427d", fg="white", bd=3,
                                  command=self.signup, relief=tk.SOLID, width=10, height=2)
        signup_button.place(relx=0.28, rely=0.6, anchor=tk.CENTER)

        login_button = tk.Button(self.current_frame, text="Login", bg="#08a64f", fg="white", bd=3,
                                 relief=tk.SOLID, command=self.login, width=10, height=2)
        login_button.place(relx=.72, rely=0.6, anchor=tk.CENTER)

        # labels
        label_dice = tk.Label(self.current_frame, text="DICE", font=("Rubik", 10, "bold", "underline"), fg="white",
                              bg=BACKGROUND_COLOR)
        label_description = tk.Label(self.current_frame, text="~Discord Integrated Cryptographic Engine",
                                     font=("Rubik", 9, "bold"), fg="white", bg=BACKGROUND_COLOR)
        label_description.pack(side=tk.BOTTOM, anchor=tk.W)
        label_dice.pack(side=tk.BOTTOM, anchor=tk.W)

    def login(self):
        pass

    def signup(self):
        pass


def main():
    root = tk.Tk()
    app_controller = ManagerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
