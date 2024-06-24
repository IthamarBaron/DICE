import sqlite3

def initialize_database(db_name):
    """
    Initialize the database with necessary tables.
    :param db_name: The name of the database file.
    """
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            channel_id TEXT NOT NULL,
            file_encryption_key TEXT NOT NULL
        )
        """)

        conn.commit()
        conn.close()
        print(f"Database '{db_name}' has been initialized with the necessary tables.")
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    db_name = 'Dice-Database.db'
    initialize_database(db_name)
