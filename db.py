import sqlite3

DATABASE_NAME = "grocery.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        brand TEXT NOT NULL,
        unit_price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL,
        expiry_date TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL,
        contact_number TEXT NOT NULL,
        email_address TEXT NOT NULL,
        delivery_schedule TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("Database created successfully!")
