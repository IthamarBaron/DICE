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
               Attempt to login with provided username and password.

               :param username: The username for login.
               :param password: The password for login.
               :return: The database row if login is successful, else None.
               """
        try:
            self.cursor.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
            row = self.cursor.fetchone()
            self.conn.commit()
            return row
        except Exception as e:
            print(f"Error during login: {e} [db_name: {self.db_name}]")

    def is_username_availability(self,username):
        """
               Check if the username is available.

               :param username: The username to check.
               :return: True if the username is available, else False.
               """
        self.cursor.execute(f"SELECT * FROM users WHERE username='{username}'")
        row = self.cursor.fetchone()
        self.conn.commit()
        if row:
            return False
        return True

    def create_new_account(self, username, password, channel_id):
        """
              Create a new account with the provided username, password, and channel ID.

              :param username: The username for the new account.
              :param password: The password for the new account.
              :param channel_id: The channel ID associated with the new account.
              """
        try:
            self.cursor.execute(f"INSERT INTO users VALUES ('{username}', '{password}', '{channel_id}')")
            self.create_new_file_table(channel_id)
        except Exception as e:
            print(f"Error creating a new account: {e}")
        finally:
            self.conn.commit()

    def create_new_file_table(self, channel_id):
        """
               Create a new file table for the specified channel ID.

               :param channel_id: The channel ID for which to create the file table.
               """
        try:
            self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS _{channel_id} (
                                filename TEXT,
                                message_id INTEGER
                                )""")
        except Exception as e:
            print(f"Error during new table creation: {e}")
            pass

    def new_file_in_channel(self, filename, message_id, channel_id):
        """
        Insert a new file record into the specified channel's file table.

        :param filename: The name of the file.
        :param message_id: The message ID associated with the file.
        :param channel_id: The channel ID where the file is stored.
        """
        try:
            self.cursor.execute(f"INSERT INTO _{channel_id} VALUES ('{filename}', '{message_id}')")
        except Exception as e:
            print(f"Error inserting a new file: {e}")
        finally:
            self.conn.commit()

    def get_files_from_id(self, channel_id):
        """
                Retrieve all file records from the specified channel's file table.

                :param channel_id: The channel ID from which to retrieve the files.
                :return: A list of file records.
                """
        try:
            self.cursor.execute(f"SELECT * FROM _{channel_id}")
            files = self.cursor.fetchall()
            self.conn.commit()
            return files
        except Exception as e:
            print(f"Error getting files from id: {e}")
            self.conn.commit()

    def get_message_id_by_name(self, filename, channel_id):
        """
              Retrieve the message ID for the specified file name and channel ID.

              :param filename: The name of the file.
              :param channel_id: The channel ID where the file is stored.
              :return: The message ID associated with the file, or 0 if not found.
              """
        try:
            self.cursor.execute(f"SELECT * FROM _{channel_id} WHERE filename='{filename}'")
            info = self.cursor.fetchone()
            message_id = info[1]
            self.conn.commit()
            return int(message_id)
        except Exception as e:
            print(f"Error getting messageID: {e}")
            self.conn.commit()
            return 0

    def delete_file_in_table(self, filename, channel_id):
        """
                Delete the file record from the specified channel's file table.

                :param filename: The name of the file to delete.
                :param channel_id: The channel ID where the file is stored.
                """
        try:
            self.cursor.execute(f"DELETE FROM _{channel_id} WHERE filename='{filename}'")
            self.conn.commit()
        except Exception as e:
            print(f"Error deleting file {e}")

