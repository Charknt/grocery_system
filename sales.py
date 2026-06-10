from product import view_products
from staff import view_staff
from db import get_connection
from datetime import datetime




# CREATE
def add_sale():

    if not view_products():
        print("Add products first before recording a sale.\n")
        return

    if not view_staff():
        print("Add staff first before recording a sale.\n")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        try:
            product_id = int(input("Enter Product ID: "))

            staff_id = int(input("Enter Staff ID: "))

            quantity_sold = int(input("Quantity sold: "))

            if quantity_sold <= 0:
                print("Quantity must be greater than zero.\n")
                return

        except ValueError:
            print("Invalid input.\n")
            return

        sale_date = input("Sale date (YYYY-MM-DD): ").strip()

        if not sale_date:
            print("Sale date cannot be empty.\n")
            return

        try:
            datetime.strptime(sale_date, "%Y-%m-%d")

        except ValueError:
            print("Invalid date format.\n")
            return

        # Check Product
        cursor.execute(
            """
            SELECT product_name, unit_price, stock_quantity
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
        stock_quantity = product[2]

        if stock_quantity <= 0:
            print("Product is out of stock.\n")
            return

        # Check stock
        if quantity_sold > stock_quantity:
            print(
                f"Insufficient stock."
                f"\nAvailable stock: {stock_quantity}\n"
            )
            return
        
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


        # Calculate total amount
        total_amount = unit_price * quantity_sold

        print(
            f"\nSummary:"
            f"\nSale Date: {sale_date}"
            f"\nProduct: {product_name}"
            f"\nStaff: {staff_name}"
            f"\nQuantity Sold: {quantity_sold}"
            f"\nTotal Amount: ₱{total_amount:.2f}"
        )


        confirm = input("\nSave sale? (Y/N): ").strip().upper()


        if confirm != "Y":
            print("Sale cancelled.\n")
            return


        # Insert sale
        cursor.execute(
            """
            INSERT INTO sales(
                sale_date,
                quantity_sold,
                total_amount,
                staff_id,
                product_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                sale_date,
                quantity_sold,
                total_amount,
                staff_id,
                product_id
            )
        )


        # Deduct stock quantity
        cursor.execute(
            """
            UPDATE products
            SET stock_quantity =
                stock_quantity - ?
            WHERE product_id = ?
            """,
            (
                quantity_sold,
                product_id
            )
        )


        conn.commit()

        print("Sale recorded successfully!\n")
        print(f"Total Amount: ₱{total_amount:.2f}\n")


    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")

    finally:
        conn.close()


# READ
def view_sales():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                s.sale_id,
                p.product_name,
                CASE
                    WHEN st.middle_initial IS NOT NULL
                        AND st.middle_initial != ''
                    THEN st.first_name || ' ' || st.middle_initial || '. ' || st.last_name
                    ELSE st.first_name || ' ' || st.last_name
                END,
                s.quantity_sold,
                s.total_amount,
                s.sale_date
            FROM sales s
            JOIN products p
                ON s.product_id = p.product_id
            JOIN staffs st
                ON s.staff_id = st.staff_id
            ORDER BY s.sale_id
        """)

        sales = cursor.fetchall()

        if not sales:
            print("No sales records found.\n")
            return False

        print("\n=== SALES LIST ===")

        for sale in sales:
            print(
                f"\nSale ID: {sale[0]}"
                f"\nProduct: {sale[1]}"
                f"\nStaff: {sale[2]}"
                f"\nQuantity Sold: {sale[3]}"
                f"\nTotal Amount: ₱{sale[4]:.2f}"
                f"\nSale Date: {sale[5]}"
            )

        print()

        return True


    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()


# UPDATE
def update_sale():

    if not view_sales():
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        try:
            sale_id = int(input("Enter Sale ID to update: "))


        except ValueError:
            print("Invalid Sale ID.\n")
            return

        # Check sale
        cursor.execute(
            """
            SELECT
                product_id,
                quantity_sold
            FROM sales
            WHERE sale_id = ?
            """,
            (sale_id,)
        )

        sale = cursor.fetchone()

        if not sale:
            print("Sale not found.\n")
            return

        product_id = sale[0]
        old_quantity = sale[1]

        # New quantity
        try:
            new_quantity = int(input("New quantity sold: "))


            if new_quantity <= 0:
                print("Quantity must be greater than zero.\n")
                return

        except ValueError:
            print("Invalid quantity.\n")
            return

        # New date
        new_date = input("New sale date (YYYY-MM-DD): ").strip()

        if not new_date:
            print("Sale date cannot be empty.\n")
            return

        try:
            datetime.strptime(new_date, "%Y-%m-%d")

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
        quantity_difference = new_quantity - old_quantity

        new_stock = current_stock + old_quantity - new_quantity

        if new_stock < 0:
            print(
                "\nCannot update sale."
                f"\nCurrent Stock: {current_stock}"
                f"\nOld Quantity: {old_quantity}"
                f"\nNew Quantity: {new_quantity}"
                "\nStock would become negative.\n"
            )
            return

        new_total_amount = unit_price * new_quantity

        # Summary
        print(
            f"\nSummary:"
            f"\nProduct: {product_name}"
            f"\nOld Quantity: {old_quantity}"
            f"\nNew Quantity: {new_quantity}"
            f"\nProjected Stock: {new_stock}"
            f"\nNew Total Amount: ₱{new_total_amount:.2f}"
        )

        confirm = input("\nSave changes? (Y/N): ").strip().upper()

        if confirm != "Y":
            print("Update cancelled.\n")
            return

        # Update sale
        cursor.execute(
            """
            UPDATE sales
            SET
                quantity_sold = ?,
                total_amount = ?,
                sale_date = ?
            WHERE sale_id = ?
            """,
            (
                new_quantity,
                new_total_amount,
                new_date,
                sale_id
            )
        )

        # Update stock
        cursor.execute(
            """
            UPDATE products
            SET stock_quantity =
                stock_quantity - ?
            WHERE product_id = ?
            """,
            (
                quantity_difference,
                product_id
            )
        )

        conn.commit()

        print("Sale updated successfully!\n")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")

    finally:
        conn.close()


# DELETE
def delete_sale():

    if not view_sales():
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        try:
            sale_id = int(input("Enter Sale ID to delete: "))

        except ValueError:
            print("Invalid Sale ID.\n")
            return

        cursor.execute(
            """
            SELECT
                product_id,
                quantity_sold
            FROM sales
            WHERE sale_id = ?
            """,
            (sale_id,)
        )

        sale = cursor.fetchone()

        if not sale:
            print("Sale not found.\n")
            return

        product_id = sale[0]
        quantity_sold = sale[1]

        print(
            f"\nSale Quantity: {quantity_sold}"
            f"\nStock will be restored after deletion."
        )

        confirm = input("\nDelete this sale? (Y/N): ").strip().upper()

        if confirm != "Y":
            print("Deletion cancelled.\n")
            return

        # Restore stock
        cursor.execute(
            """
            UPDATE products
            SET stock_quantity =
                stock_quantity + ?
            WHERE product_id = ?
            """,
            (
                quantity_sold,
                product_id
            )
        )

        # Delete sale record
        cursor.execute(
            """
            DELETE FROM sales
            WHERE sale_id = ?
            """,
            (sale_id,)
        )

        conn.commit()

        print("Sale deleted successfully!\n")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

    finally:
        conn.close()


# SEARCH
def search_sale():

    keyword = input("Enter sale date (YYYY-MM-DD): ").strip()

    if not keyword:
        print("Search keyword cannot be empty.\n")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                s.sale_id,
                p.product_name,
                CASE
                    WHEN st.middle_initial IS NOT NULL
                        AND st.middle_initial != ''
                    THEN st.first_name || ' ' || st.middle_initial || '. ' || st.last_name
                    ELSE st.first_name || ' ' || st.last_name
                END,
                s.quantity_sold,
                s.total_amount,
                s.sale_date
            FROM sales s
            JOIN products p
                ON s.product_id = p.product_id
            JOIN staffs st
                ON s.staff_id = st.staff_id
            WHERE s.sale_date LIKE ?
            ORDER BY s.sale_id
        """,
        (f"%{keyword}%",))

        sales = cursor.fetchall()

        if not sales:
            print("No sales found.\n")
            return

        print("\n=== SEARCH RESULT ===")

        for sale in sales:

            print(
                f"\nSale ID: {sale[0]}"
                f"\nProduct: {sale[1]}"
                f"\nStaff: {sale[2]}"
                f"\nQuantity Sold: {sale[3]}"
                f"\nTotal Amount: ₱{sale[4]:.2f}"
                f"\nSale Date: {sale[5]}"
            )

        print()

    finally:
        conn.close()
