import sqlite3

conn = sqlite3.connect('Dice-Database.db')
cursor = conn.cursor()


conn.commit()
conn.close()
