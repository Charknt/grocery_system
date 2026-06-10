from product import view_products
from supplier import view_supplier
from staff import view_staff
from db import get_connection
from datetime import datetime

# CREATE
def add_delivery():

    if not view_products():
        print("Add products first before recording delivery.\n")
        return

    if not view_supplier():
        print("Add supplier first before recording delivery.\n")
        return

    if not view_staff():
        print("Add staff first before recording delivery.\n")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        try:

            product_id = int(input("Enter Product ID: "))
            
            supplier_id = int(input("Enter Supplier ID: "))
            
            staff_id = int(input("Enter Staff ID: "))

            quantity_received = int(input("Quantity received: "))

            if quantity_received <= 0:
                print("Quantity must be greater than zero.\n")
                return
            
        except ValueError:
            print("Invalid input.\n")
            return

        delivery_date = input("Delivery date (YYYY-MM-DD): ").strip()

        if not delivery_date:
            print("Delivery date cannot be empty.\n")
            return

        try:
            datetime.strptime(delivery_date,"%Y-%m-%d")

        except ValueError:
            print("Invalid date format.\n")
            return

        # Check Product

        cursor.execute(
            """
            SELECT product_name, unit_price
            FROM products
            WHERE product_id = ?
            """,
            (product_id,)
        )

        product = cursor.fetchone()

        if not product:
            print("Product not found.\n")
            return
                
        product_name = product[0]
        unit_price = product[1]

        # Check Supplier

        cursor.execute(
            """
            SELECT supplier_name
            FROM suppliers
            WHERE supplier_id = ?
            """,
            (supplier_id,)
        )
        
        supplier = cursor.fetchone()

        if not supplier:
            print("Supplier not found.\n")
            return
    
        supplier_name = supplier[0]

        # Check Staff

        cursor.execute(
            """
            SELECT first_name, middle_initial, last_name
            FROM staffs
            WHERE staff_id = ?
            """,
            (staff_id,)
        )

        staff = cursor.fetchone()

        if not staff:
            print("Staff not found.\n")
            return

        staff_name = (
            f"{staff[0]} {staff[1]}. {staff[2]}"
            if staff[1]
            else f"{staff[0]} {staff[2]}"
        )

        # Calculate total cost

        total_cost = (unit_price * quantity_received)

        print(
            f"\nSummary:"
            f"\nDelivery Date: {delivery_date}"
            f"\nProduct: {product_name}"
            f"\nSupplier: {supplier_name}"
            f"\nStaff: {staff_name}"
            f"\nQuantity Received: {quantity_received}"
            f"\nTotal Cost: ₱{total_cost:.2f}"
        )

        confirm = input("\nSave delivery? (Y/N): ").strip().upper()

        if confirm != "Y":
            print("Delivery cancelled.\n")
            return

        # Insert delivery

        cursor.execute(
            """
            INSERT INTO deliveries(
                delivery_date,
                quantity_received,
                total_cost,
                supplier_id,
                product_id,
                staff_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                delivery_date,
                quantity_received,
                total_cost,
                supplier_id,
                product_id,
                staff_id
            )
        )

        # Update stock quantity

        cursor.execute(
            """
            UPDATE products
            SET stock_quantity =
                stock_quantity + ?
            WHERE product_id = ?
            """,
            (
                quantity_received,
                product_id
            )
        )

        conn.commit()

        print("Delivery recorded successfully!\n")
        print(f"Total Cost: ₱{total_cost:.2f}\n")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    
    finally:
        conn.close()


# READ
def view_delivery():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                d.delivery_id,
                p.product_name,
                s.supplier_name,
                CASE
                    WHEN st.middle_initial IS NOT NULL
                        AND st.middle_initial != ''
                    THEN st.first_name || ' ' || st.middle_initial || '. ' || st.last_name
                    ELSE st.first_name || ' ' || st.last_name
                END,
                d.quantity_received,
                d.total_cost,
                d.delivery_date
            FROM deliveries d
            JOIN products p
                ON d.product_id = p.product_id
            JOIN suppliers s
                ON d.supplier_id = s.supplier_id
            JOIN staffs st
                ON d.staff_id = st.staff_id
            ORDER BY d.delivery_id
        """)        
        deliveries = cursor.fetchall()

        if not deliveries:
            print("No delivery records found.\n")
            return False

        print("\n=== DELIVERY LIST ===")

        for delivery in deliveries:
            print(
                f"\nDelivery ID: {delivery[0]}"
                f"\nProduct: {delivery[1]}"
                f"\nSupplier: {delivery[2]}"
                f"\nStaff: {delivery[3]}"
                f"\nQuantity Received: {delivery[4]}"
                f"\nTotal Cost: ₱{delivery[5]:.2f}"
                f"\nDelivery Date: {delivery[6]}"
            )

        print()

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False
    
    finally:
        conn.close()


# UPDATE
def update_delivery():

    if not view_delivery():
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        try:
            delivery_id = int(input("Enter Delivery ID to update: "))

        except ValueError:
            print("Invalid Delivery ID.\n")
            return

        # Check delivery

        cursor.execute(
            """
            SELECT
                product_id,
                quantity_received
            FROM deliveries
            WHERE delivery_id = ?
            """,
            (delivery_id,)
        )

        delivery = cursor.fetchone()

        if not delivery:
            print("Delivery not found.\n")
            return

        product_id = delivery[0]
        old_quantity = delivery[1]

        # New quantity

        try:
            new_quantity = int(input("New quantity received: "))

            if new_quantity <= 0:
                print("Quantity must be greater than zero.\n")
                return

        except ValueError:
            print("Invalid quantity.\n")
            return

        # New date

        new_date = input("New delivery date (YYYY-MM-DD): ").strip()

        if not new_date:
            print("Delivery date cannot be empty.\n")
            return

        try:
            datetime.strptime( new_date,"%Y-%m-%d")

        except ValueError:
            print("Invalid date format.\n")
            return

        # Get product info

        cursor.execute(
            """
            SELECT
                product_name,
                unit_price,
                stock_quantity
            FROM products
            WHERE product_id = ?
            """,
            (product_id,)
        )

        product = cursor.fetchone()

        if not product:
            print("Product not found.\n")
            return

        product_name = product[0]
        unit_price = product[1]
        current_stock = product[2]

        # Calculations

        quantity_difference = (new_quantity - old_quantity)

        new_stock = (current_stock + quantity_difference)

        if new_stock < 0:
            print(
                "\nCannot update delivery."
                f"\nCurrent Stock: {current_stock}"
                f"\nOld Quantity: {old_quantity}"
                f"\nNew Quantity: {new_quantity}"
                "\nStock would become negative.\n"
            )
            return

        new_total_cost = (unit_price * new_quantity)

        # Summary

        print(
            f"\nSummary:"
            f"\nProduct: {product_name}"
            f"\nOld Quantity: {old_quantity}"
            f"\nNew Quantity: {new_quantity}"
            f"\nProjected Stock: {new_stock}"
            f"\nNew Total Cost: ₱{new_total_cost:.2f}"
        )

        confirm = input("\nSave changes? (Y/N): ").strip().upper()

        if confirm != "Y":
            print("Update cancelled.\n")
            return

        # Update delivery

        cursor.execute(
            """
            UPDATE deliveries
            SET
                quantity_received = ?,
                total_cost = ?,
                delivery_date = ?
            WHERE delivery_id = ?
            """,
            (
                new_quantity,
                new_total_cost,
                new_date,
                delivery_id
            )
        )

        # Update stock

        cursor.execute(
            """
            UPDATE products
            SET stock_quantity =
                stock_quantity + ?
            WHERE product_id = ?
            """,
            (
                quantity_difference,
                product_id
            )
        )

        conn.commit()

        print("Delivery updated successfully!\n")

    except Exception as e:

        conn.rollback()

        print(f"Error: {e}")

    finally:

        conn.close()


# DELETE
def delete_delivery():

    if not view_delivery():
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        try:
            delivery_id = int(input("Enter Delivery ID to delete: "))

        except ValueError:
            print("Invalid Delivery ID.\n")
            return

        cursor.execute(
            """
            SELECT
                product_id,
                quantity_received
            FROM deliveries
            WHERE delivery_id = ?
            """,
            (delivery_id,)
        )

        delivery = cursor.fetchone()

        if not delivery:
            print("Delivery not found.\n")
            return

        product_id = delivery[0]
        quantity_received = delivery[1]

        # Check current stock

        cursor.execute(
            """
            SELECT stock_quantity
            FROM products
            WHERE product_id = ?
            """,
            (product_id,)
        )

        product = cursor.fetchone()

        if not product:
            print("Product not found.\n")
            return

        current_stock = product[0]

        if current_stock < quantity_received:
            print(
                f"\nCannot delete delivery."
                f"\nCurrent Stock: {current_stock}"
                f"\nDelivery Quantity: {quantity_received}"
                f"\nStock would become negative.\n"
            )
            return

        print(
            f"\nQuantity to remove from stock: "
            f"{quantity_received}"
        )


        confirm = input("\nDelete this delivery? (Y/N): ").strip().upper()

        if confirm != "Y":
            print("Deletion cancelled.\n")
            return

        # Remove stock added by delivery

        cursor.execute(
            """
            UPDATE products
            SET stock_quantity =
                stock_quantity - ?
            WHERE product_id = ?
            """,
            (
                quantity_received,
                product_id
            )
        )

        # Delete delivery record

        cursor.execute(
            """
            DELETE FROM deliveries
            WHERE delivery_id = ?
            """,
            (delivery_id,)
        )

        conn.commit()

        print("Delivery deleted successfully!\n")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
       
    finally:
        conn.close()


# SEARCH
def search_delivery():

    keyword = input(
        "Enter delivery date (YYYY-MM-DD): "
    ).strip()

    if not keyword:
        print("Search keyword cannot be empty.\n")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                d.delivery_id,
                p.product_name,
                s.supplier_name,
                CASE
                    WHEN st.middle_initial IS NOT NULL
                    AND st.middle_initial != ''
                    THEN st.first_name || ' ' ||
                         st.middle_initial || '. ' ||
                         st.last_name
                    ELSE st.first_name || ' ' ||
                         st.last_name
                END,
                d.quantity_received,
                d.total_cost,
                d.delivery_date
            FROM deliveries d
            JOIN products p
                ON d.product_id = p.product_id
            JOIN suppliers s
                ON d.supplier_id = s.supplier_id
            JOIN staffs st
                ON d.staff_id = st.staff_id
            WHERE d.delivery_date LIKE ?
            ORDER BY d.delivery_id
        """,
        (f"%{keyword}%",)
        )

        deliveries = cursor.fetchall()

        if not deliveries:
            print("No delivery records found.\n")
            return

        print("\n=== SEARCH RESULT ===")

        for delivery in deliveries:

            print(
                f"\nDelivery ID: {delivery[0]}"
                f"\nProduct: {delivery[1]}"
                f"\nSupplier: {delivery[2]}"
                f"\nStaff: {delivery[3]}"
                f"\nQuantity Received: {delivery[4]}"
                f"\nTotal Cost: ₱{delivery[5]:.2f}"
                f"\nDelivery Date: {delivery[6]}"
            )

        print()

    finally:
        conn.close()
