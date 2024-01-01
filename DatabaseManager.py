import sqlite3


class Database:

    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def attempt_login(self, username, password):
        try:
            self.cursor.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
            row = self.cursor.fetchone()
            self.conn.commit()
            return row
        except Exception as e:
            print(f"Error during login: {e}")

    def is_username_availability(self,username):
        self.cursor.execute(f"SELECT * FROM users WHERE username='{username}'")
        row = self.cursor.fetchone()
        self.conn.commit()
        if row:
            return False
        return True

    def create_new_account(self, username, password, channel_id):
        try:
            self.cursor.execute(f"INSERT INTO users VALUES ('{username}', '{password}', '{channel_id}')")
            self.create_new_file_table(channel_id)
        except Exception as e:
            print(f"Error creating a new account: {e}")
        finally:
            self.conn.commit()

    def create_new_file_table(self, channel_id):
        try:
            self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS _{channel_id} (
                                filename TEXT,
                                message_id INTEGER
                                )""")
        except Exception as e:
            print(f"Error during new table creation: {e}")
            pass

    def new_file_in_channel(self, filename, message_id, channel_id):
        try:
            self.cursor.execute(f"INSERT INTO _{channel_id} VALUES ('{filename}', '{message_id}')")
        except Exception as e:
            print(f"Error inserting a new file: {e}")
        finally:
            self.conn.commit()

