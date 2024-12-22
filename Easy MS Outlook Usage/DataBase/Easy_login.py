import sqlite3

# Connect to (or create) a database
connection = sqlite3.connect("DataBase/example.db")
print("Database connected successfully!")

cursor = connection.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    UserName INTEGER PRIMARY KEY,
    microsoft_key TEXT NOT NULL
)
''')

connection.commit()