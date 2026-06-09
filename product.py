from db import get_connection
from datetime import datetime

CATEGORIES = [
    "Canned Goods",
    "Snacks",
    "Drinks",
    "Instant Noodles",
    "Toiletries",
    "Cleaning Supplies",
    "Household",
    "Others"
]

# CREATE
def add_product():

    conn = get_connection()
    cursor = conn.cursor()

    try:
        product_name = input("Enter product name: ").strip()

        if not product_name:
            print("Product name cannot be empty.\n")
            return
        
        cursor.execute(
            """
            SELECT * FROM products
            WHERE LOWER(product_name) = LOWER(?)
            """,
            (product_name,)
        )

        if cursor.fetchone():
            print("Product already exists.\n")
            return
        
        print("\nAvailable Categories:")

        for i, category in enumerate(CATEGORIES, start=1):
            print(f"{i}. {category}")

        try:
            category_choice = int(input("Choose category: "))
            category = CATEGORIES[category_choice - 1]

        except (ValueError, IndexError):
            print("Invalid category.\n")
            return

        brand = input("Enter brand: ").strip()

        if not brand:
            print("Brand cannot be empty.\n")
            return

        expiry_date = input("Enter expiry date (YYYY-MM-DD): ").strip()

        if not expiry_date:
            print("Expiry date cannot be empty.\n")
            return

        try:
            datetime.strptime(expiry_date, "%Y-%m-%d")

        except ValueError:
            print("Invalid date format.\n")
            return

        try:
            unit_price = float(input("Enter unit price: "))

            stock_quantity = int(input("Enter stock quantity: "))

        except ValueError:
            print("Invalid input.\n")
            return

        if unit_price <= 0:
            print("Price must be greater than zero.\n")
            return

        if stock_quantity < 0:
            print("Quantity cannot be negative.\n")
            return

        cursor.execute(
            """
            INSERT INTO products(
                product_name,
                category,
                brand,
                expiry_date,
                unit_price,
                stock_quantity
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                product_name,
                category,
                brand,
                expiry_date,
                unit_price,
                stock_quantity
            )
        )

        conn.commit()

        print("Product added successfully!\n")

    finally:
        conn.close()

# READ
def view_products():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

        if not products:
            print("There are no products. Please add a product first.\n")
            return False

        print("\n=== PRODUCT LIST ===")

        for product in products:
            print(
                f"{product[0]} | "
                f"Product name: {product[1]} | "
                f"Category: {product[2]} | "
                f"Brand: {product[3]} | "
                f"Unit Price: ₱{product[4]:.2f} | "
                f"Stock: {product[5]} | "
                f"Expiry: {product[6]}"
            )

        print()

        return True

    finally:
        conn.close()

#UPDATE
def update_product():

    if not view_products():
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        try:
            product_id = int(input("Enter product ID to update: "))

        except ValueError:
            print("Invalid product ID.\n")
            return

        cursor.execute(
            """
            SELECT * FROM products
            WHERE product_id = ?
            """,
            (product_id,)
        )

        if not cursor.fetchone():
            print("Product not found.\n")
            return

        new_name = input("New product name: ").strip()

        if not new_name:
            print("Product name cannot be empty.\n")
            return

        print("\nAvailable Categories:")

        for i, category in enumerate(CATEGORIES, start=1):
            print(f"{i}. {category}")

        try:
            category_choice = int(input("Choose new category: "))
            new_category = CATEGORIES[category_choice - 1]

        except (ValueError, IndexError):
            print("Invalid category.\n")
            return

        new_brand = input("New brand: ").strip()

        if not new_brand:
            print("Brand cannot be empty.\n")
            return

        new_expiry_date = input("New expiry date (YYYY-MM-DD): ").strip()

        if not new_expiry_date:
            print("Expiry date cannot be empty.\n")
            return

        try:
            datetime.strptime(new_expiry_date,"%Y-%m-%d")

        except ValueError:
            print("Invalid date format.\n")
            return

        try:
            new_price = float(input("New price: "))

        except ValueError:
            print("Invalid price or quantity.\n")
            return

        if new_price <= 0:
            print("Price must be greater than zero.\n")
            return

        cursor.execute(
            """
            UPDATE products
            SET
                product_name = ?,
                category = ?,
                brand = ?,
                unit_price = ?,
                expiry_date = ?
            WHERE product_id = ?
            """,
            (
                new_name,
                new_category,
                new_brand,
                new_price,
                new_expiry_date,
                product_id
            )
        )

        conn.commit()

        print("Product updated successfully!\n")

    finally:
        conn.close()


# DELETE 
def delete_product():

    if not view_products():
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        try:
            product_id = int(input("Enter product ID to delete: "))

        except ValueError:
            print("Invalid product ID.\n")
            return
        
        cursor.execute(
            """
            SELECT *
            FROM deliveries
            WHERE product_id = ?
            """,
            (product_id,)
        )

        if cursor.fetchone():
            print(
                "Cannot delete product. "
                "Product is used in delivery records.\n"
            )
            return

        cursor.execute(
            """
            DELETE FROM products
            WHERE product_id = ?
            """,
            (product_id,)
        )

        conn.commit()

        if cursor.rowcount > 0:
            print("Product deleted successfully!\n")

        else:
            print("Product not found.\n")

    except ValueError:
        print("Invalid input.\n")

    finally:
        conn.close()
