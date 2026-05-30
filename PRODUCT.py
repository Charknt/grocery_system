import sqlite3

conn = sqlite3.connect("grocery.db")
cursor = conn.cursor()

# CREATE
def add_product():
    name = input("Enter product name: ").strip()

    if not name:
        print("Product name cannot be empty.")
        return
    
    try:
        price = float(input("Enter price: "))
        quantity = int(input("Enter quantity: "))

        cursor.execute(
            "SELECT * FROM products WHERE name = ?",
            (name,)
        )

        if cursor.fetchone():
            print("Product already exists.")
            return

        if price < 0:
            print("The price cannot be negative value")
            return
        
        if quantity < 0:
            print("The quantity cannot be negative")
            return        

        cursor.execute(
            """
            INSERT INTO products(name, price, quantity)
            VALUES (?, ?, ?)
            """,
            (name, price, quantity)
        )



        conn.commit()

        print("Product added successfully!\n")

    except ValueError:
        print("Invalid input.\n")


# READ
def view_products():

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    if not products:
        print("There are no products. Please add a product first.\n")
        return False

    print("\n=== PRODUCT LIST ===")

    for product in products:

        print(
            f"{product[0]}. {product[1]} | "
            f"Price: ₱{product[2]:.2f} | "
            f"Stock: {product[3]}"
        )

    print()

    return True

# UPDATE
def update_product():

    if not view_products():
        return
    
    try:

        product_id = int(
            input("Enter product ID to update: ")
        )

        new_name = input("New name: ").strip()

        if not new_name:
            print("Product name cannot be empty.")
            return        
        
        new_price = float(input("New price: "))
        new_quantity = int(input("New quantity: "))

        if new_price < 0:
            print("Price cannot be negative value.")
            return

        if new_quantity < 0:
            print("Quantity cannot be negative.")
            return

        cursor.execute(
            """
            UPDATE products
            SET name = ?, price = ?, quantity = ?
            WHERE id = ?
            """,
            (new_name, new_price, new_quantity, product_id)
        )

        conn.commit()

        if cursor.rowcount > 0:
            print("Product updated successfully!\n")
        else:
            print("Product not found.\n")

    except ValueError:
        print("Invalid input.\n")

# DELETE
def delete_product():

    if not view_products():
        return

    try:

        product_id = int(
            input("Enter product ID to delete: ")
        )

        cursor.execute(
            """
            DELETE FROM products
            WHERE id = ?
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


# MAIN MENU
while True:
    print("=== GROCERY INVENTORY SYSTEM ===")
    print("1. Add Product")
    print("2. View Products")
    print("3. Update Product")
    print("4. Delete Product")
    print("5. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        add_product()

    elif choice == "2":
        view_products()

    elif choice == "3":
        update_product()

    elif choice == "4":
        delete_product()

    elif choice == "5":
        conn.close()
        print("Thank you for using the system!")
        break

    else:
        print("Invalid choice.\n")
