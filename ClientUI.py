import os
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
        self.client_instance = None  # type: Client
        self.connect_frame()
        self.display_files = []

    # region FRAMES

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

        self.error_label_0 = tk.Label(self.current_frame, text="", font=("Arial", 12, "bold"), fg="#cf3e3e",
                                    bg=BACKGROUND_COLOR)

        self.error_label_0.pack()

        # Connect Button
        connect_button = tk.Button(self.current_frame, text="Connect", command=self.connect_to_server, bg="#4CAF50",
                                   fg="black",
                                   bd=2, relief="solid", width=15, height=2)
        connect_button.pack(pady=20)


        # labels
        label_dice = tk.Label(self.current_frame, text="DICE", font=("Rubik", 10, "bold", "underline"), fg="white",
                              bg=BACKGROUND_COLOR)
        label_description = tk.Label(self.current_frame, text="~Discord Integrated Cryptographic Engine",
                                     font=("Rubik", 9, "bold"), fg="white", bg=BACKGROUND_COLOR)
        label_description.pack(side=tk.BOTTOM, anchor=tk.W)
        label_dice.pack(side=tk.BOTTOM, anchor=tk.W)

    def login_signup_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.current_frame.pack(expand=True, fill=tk.BOTH)
        self.root.geometry("500x400")

        # Title
        title_label = tk.Label(self.current_frame, text="LOG IN/SIGN UP", font=("Rubik", 25, "bold"),
                               bg=BACKGROUND_COLOR, fg="white")
        title_label.pack(side=tk.TOP, pady=20)

        # Username Section
        username_label = tk.Label(self.current_frame, text="Name", font=("Arial", 12, "bold"), bg=BACKGROUND_COLOR,
                                  fg="black")
        username_label.pack(side=tk.TOP, padx=20, pady=(0, 0))

        self.username_entry = tk.Entry(self.current_frame, bg="#D3D3D3", fg="#1f1f1f", bd=2, insertbackground="black",
                                       width=45
                                       , relief=tk.SOLID, )
        self.username_entry.insert(0, "Enter username")
        self.username_entry.pack(side=tk.TOP, padx=20, pady=(0, 10), ipady=5)

        # Password Section
        password_label = tk.Label(self.current_frame, text="Password", font=("Arial", 12, "bold"), bg=BACKGROUND_COLOR,
                                  fg="black")
        password_label.pack(side=tk.TOP, padx=20, pady=(0, 0))

        self.password_entry = tk.Entry(self.current_frame, show="*", bg="#D3D3D3", fg="#1f1f1f", bd=2,
                                       insertbackground="black",
                                       width=45, relief=tk.SOLID)
        self.password_entry.pack(side=tk.TOP, padx=20, pady=(0, 10), ipady=5)

        self.error_label = tk.Label(self.current_frame, text="", font=("Arial", 12, "bold"), fg="#cf3e3e",
                                    bg=BACKGROUND_COLOR)
        self.error_label.pack()

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

    def main_application_frame(self):

        self.initiate_users_files()

        self.current_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.root.title("File Upload")

        # title
        self.title_label = tk.Label(self.root, text="DICE - Debug panel", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # file upload button
        self.upload_button = tk.Button(self.root, text="Upload File", command=self.upload_file)
        self.upload_button.pack(pady=20)

        # send button
        self.send_button = tk.Button(self.root, text="Send", command=self.send_data)
        self.send_button.pack(pady=20)

        # reload button
        self.reload_files_button = tk.Button(self.root, text="Refresh Files", command=self.reload_files)
        self.reload_files_button.pack(anchor="se")
        self.reload_files_buttont = tk.Button(self.root, text="CLEAR Files", command=self.clear_file_labels)
        self.reload_files_buttont.pack(anchor="se")
        self.reload_files_buttontt = tk.Button(self.root, text="INNIT Files", command=self.initiate_users_files)
        self.reload_files_buttontt.pack(anchor="se")
        self.reload_files_buttontt = tk.Button(self.root, text="INSTANTIATE Files",
                                               command=self.instantiate_file_labels)
        self.reload_files_buttontt.pack(anchor="se")

        self.instantiate_file_labels()
        self.root.after(200, self.check_reload_flag)


    # endregion FRAMES

    # region COMMANDS

    def connect_to_server(self):
        ip = self.entry.get()
        print(f"Attempting to connect to: {ip}")
        self.client_instance = Client(ip, 12345)
        is_successful = self.client_instance.connect_to_server()

        if not is_successful:
            self.error_label_0.config(text="Connection failed, Try again")
            return
        self.client_instance.receive_data()
        # If connection is successful, switch to the file upload frame
        self.current_frame.destroy()
        self.login_signup_frame()

    def upload_file(self):
        self.uploded_file_path = filedialog.askopenfilename()
        file_size = os.path.getsize(self.uploded_file_path)
        file_size = file_size / (1024 ** 3)  # gb
        if file_size > 1:
            self.uploded_file_path = None
            # TODO: DISPLAY FILE LARGER ERROR
            return

    def send_data(self):
        try:
            if self.uploded_file_path:
                thread = threading.Thread(target=self.client_instance.send_file_to_server,
                                          args=(self.uploded_file_path, self.client_instance.user_data[2]), daemon=True)
                thread.start()
            print("Finished sending method!")
        except Exception as e:
            print(f"Error sending the file to the server: {e}")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        print(f"attempting login as {username} with {password}")
        self.client_instance.request_login(username, password)
        login_data = self.client_instance.user_data
        if login_data:
            self.client_instance.user_data = login_data
            #  if login is successful we move on to the app
            self.current_frame.destroy()
            self.main_application_frame()
        else:
            self.error_label.config(text="Login Failed\ninvalid credentials")
            pass

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if len(username) == 0 or len(password) == 0:
            self.error_label.config(text="SignUp Failed\nFill both fields")
            return
        is_successful = self.client_instance.request_signup(username, password)
        if is_successful:
            self.login()
        else:
            self.error_label.config(text="SignUp Failed\nName Is Taken")

    def download_file(self, filename):
        thread = threading.Thread(target=self.client_instance.request_download_file,
                                  args=(filename, int(self.client_instance.user_data[2])))
        thread.start()

    def reload_files(self):
        # Clear existing labels and buttons
        self.clear_file_labels()
        # Update underlying data (self.client_instance.users_files)
        self.initiate_users_files()
        # Instantiate new labels and buttons using updated data
        self.instantiate_file_labels()

    def delete_file(self, filename):
        print(f"deleting file {filename}")
        thread = threading.Thread(target=self.client_instance.request_file_deletion,
                                  args=(filename, int(self.client_instance.user_data[2])))
        thread.start()

    # region File-display

    def check_reload_flag(self):
        if self.client_instance.reload_files_flag:
            self.reload_files()
            self.client_instance.reload_files_flag = False
        self.root.after(20, self.check_reload_flag)


#TODO: ALSO MAKE THIS SERER SIDE
    def initiate_users_files(self):
        self.client_instance.request_user_files()
        files = self.client_instance.users_files
        self.client_instance.users_files = {}  # clearing the dict before instantiation
        for file in files:
            self.client_instance.users_files[file[0]] = file[1]

    def instantiate_file_labels(self):
        for file_name in self.client_instance.users_files.keys():
            # Frame to group components for each file
            file_frame = tk.Frame(self.root)
            file_frame.pack()

            # File Name Label
            file_label = tk.Label(file_frame, text=file_name)
            file_label.pack(side=tk.LEFT, padx=5)

            # Download Button
            download_button = tk.Button(file_frame, text="Download", fg="green",
                                        command=lambda name=file_name: self.download_file(name))
            download_button.pack(side=tk.LEFT, padx=5)

            # Delete Button
            delete_button = tk.Button(file_frame, text="Delete", fg="red",
                                      command=lambda name=file_name: self.delete_file(name))
            delete_button.pack(side=tk.LEFT, padx=5)

            self.display_files.extend([file_frame, file_label, download_button, delete_button])

    def clear_file_labels(self):
        for button in self.display_files:
            button.destroy()
        self.display_files = []

    # endregion File-display

    # endregion COMMANDS


def main():
    root = tk.Tk()
    app_controller = ManagerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()