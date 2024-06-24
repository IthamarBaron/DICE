import sqlite3

class Database:

    def __init__(self, db_name):
        """
        Initialize the database connection and cursor.
        :param db_name: The name of the database file.
        """
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def attempt_login(self, username, password):
        """
        Attempt to log in with provided username and password.
        :param username: The username for login.
        :param password: The password for login.
        :return: The database row if login is successful, else None.
        """
        try:
            query = "SELECT * FROM users WHERE username=? AND password=?"
            self.cursor.execute(query, (username, password))
            row = self.cursor.fetchone()
            return row
        except Exception as e:
            print(f"Error during login: {e} [db_name: {self.db_name}]")

    def is_username_available(self, username):
        """
        Check if the username is available.
        :param username: The username to check.
        :return: True if the username is available, else False.
        """
        try:
            query = "SELECT * FROM users WHERE username=?"
            self.cursor.execute(query, (username,))
            row = self.cursor.fetchone()
            if row:
                return False
            return True
        except Exception as e:
            print(f"Error checking username availability: {e}")
            return False

    def create_new_account(self, username, password, channel_id):
        """
        Create a new account with the provided username, password, and channel ID.
        :param username: The username for the new account.
        :param password: The password for the new account.
        :param channel_id: The channel ID associated with the new account.
        """
        try:
            query = "INSERT INTO users VALUES (?, ?, ?)"
            self.cursor.execute(query, (username, password, channel_id))
            self.create_new_file_table(channel_id)
            self.conn.commit()
        except Exception as e:
            print(f"Error creating a new account: {e}")

    def create_new_file_table(self, channel_id):
        """
        Create a new file table for the specified channel ID.
        :param channel_id: The channel ID for which to create the file table.
        """
        try:
            query = f"CREATE TABLE IF NOT EXISTS _{channel_id} (filename TEXT, message_id INTEGER)"
            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            print(f"Error during new table creation: {e}")

    def new_file_in_channel(self, filename, message_id, channel_id):
        """
        Insert a new file record into the specified channel's file table.
        :param filename: The name of the file.
        :param message_id: The message ID associated with the file.
        :param channel_id: The channel ID where the file is stored.
        """
        try:
            query = f"INSERT INTO _{channel_id} VALUES (?, ?)"
            self.cursor.execute(query, (filename, message_id))
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting a new file: {e}")

    def get_files_from_id(self, channel_id):
        """
        Retrieve all file records from the specified channel's file table.
        :param channel_id: The channel ID from which to retrieve the files.
        :return: A list of file records.
        """
        try:
            query = f"SELECT * FROM _{channel_id}"
            self.cursor.execute(query)
            files = self.cursor.fetchall()
            return files
        except Exception as e:
            print(f"Error getting files from id: {e}")
            return []

    def get_message_id_by_name(self, filename, channel_id):
        """
        Retrieve the message ID for the specified file name and channel ID.
        :param filename: The name of the file.
        :param channel_id: The channel ID where the file is stored.
        :return: The message ID associated with the file, or 0 if not found.
        """
        try:
            query = f"SELECT message_id FROM _{channel_id} WHERE filename=?"
            self.cursor.execute(query, (filename,))
            info = self.cursor.fetchone()
            if info:
                return info[0]
            return 0
        except Exception as e:
            print(f"Error getting message ID: {e}")
            return 0

    def delete_file_in_table(self, filename, channel_id):
        """
        Delete the file record from the specified channel's file table.
        :param filename: The name of the file to delete.
        :param channel_id: The channel ID where the file is stored.
        """
        try:
            query = f"DELETE FROM _{channel_id} WHERE filename=?"
            self.cursor.execute(query, (filename,))
            self.conn.commit()
        except Exception as e:
            print(f"Error deleting file: {e}")

    def __del__(self):
        """
        Destructor to close the database connection when the object is deleted.
        """
        try:
            self.conn.close()
        except Exception as e:
            print(f"Error closing database connection: {e}")