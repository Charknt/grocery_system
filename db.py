import sqlite3

conn = sqlite3.connect("grocery.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL
)
""")

conn.commit()
conn.close()

print("Database created successfully!")
