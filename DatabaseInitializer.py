import sqlite3

def initialize_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        channel_id TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    db_name = 'Dice-Database.db'
    initialize_database(db_name)
    print(f"Database '{db_name}' has been initialized with the necessary tables.")