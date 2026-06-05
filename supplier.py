from db import get_connection

DELIVERY_SCHEDULES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
    "Weekly",
    "Bi-Weekly",
    "Monthly",
    "As Needed"
]

# CREATE
def add_supplier():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        name = input("Enter Supplier name: ").strip()

        if not name:
            print("Supplier name cannot be empty.\n")
            return
        
        cursor.execute(
            """
            SELECT * FROM suppliers
            WHERE LOWER(supplier_name) = LOWER(?)
            """,
            (name,)
        )

        if cursor.fetchone():
            print("Supplier already exists.\n")
            return

        contact_number = input("Enter phone number: ").strip()

        if not contact_number:
            print("Phone number cannot be empty.\n")
            return

        email_address = input("Enter email address: ").strip()

        if not email_address:
            print("Email address cannot be empty.\n")
            return

        if "@" not in email_address:
            print("Invalid email address.\n")
            return
        
        print("\nAvailable Delivery Schedules:")

        for i, schedule in enumerate(
            DELIVERY_SCHEDULES,
            start=1
        ):
            print(f"{i}. {schedule}")

        try:
            schedule_choice = int(input("Choose delivery schedule: "))
            delivery_schedule = DELIVERY_SCHEDULES[schedule_choice - 1]

        except (ValueError, IndexError):
            print("Invalid delivery schedule.\n")
            return

        cursor.execute(
            """
            INSERT INTO suppliers(
                supplier_name,
                contact_number,
                email_address,
                delivery_schedule
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name, 
                contact_number, 
                email_address,
                delivery_schedule
            )
        )

        conn.commit()

        print("Supplier added successfully!\n")

    finally:
        conn.close()

# READ
def view_supplier():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("SELECT * FROM suppliers")
        suppliers = cursor.fetchall()

        if not suppliers:
            print("There are no suppliers. Please add supplier first.\n")
            return False

        print("\n=== SUPPLIER LIST ===")

        for supplier in suppliers:
            print(
                f"{supplier[0]}. Supplier name: {supplier[1]} | "
                f"Contact number: {supplier[2]} | "
                f"Email address: {supplier[3]} | "
                f"Delivery schedule: {supplier[4]}"
            )

        print()

        return True

    finally:
        conn.close()

# UPDATE
def update_supplier():

    if not view_supplier():
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        try:
            supplier_id = int(
                input("Enter supplier ID to update: ")
            )

        except ValueError:
            print("Invalid supplier ID.\n")
            return

        cursor.execute(
            """
            SELECT * FROM suppliers
            WHERE supplier_id = ?
            """,
            (supplier_id,)
        )

        if not cursor.fetchone():
            print("Supplier not found.\n")
            return

        new_name = input("New supplier name: ").strip()

        if not new_name:
            print("Supplier name cannot be empty.\n")
            return

        new_contact_number = input(
            "New contact number: "
        ).strip()

        if not new_contact_number:
            print("Contact number cannot be empty.\n")
            return

        new_email_address = input(
            "New email address: "
        ).strip()

        if not new_email_address:
            print("Email address cannot be empty.\n")
            return

        if "@" not in new_email_address:
            print("Invalid email address.\n")
            return
        
        print("\nAvailable Delivery Schedules:")

        for i, schedule in enumerate(
            DELIVERY_SCHEDULES,
            start=1
        ):
            print(f"{i}. {schedule}")

        try:
            schedule_choice = int(input("Choose new delivery schedule: "))
            new_delivery_schedule = DELIVERY_SCHEDULES[schedule_choice - 1]

        except (ValueError, IndexError):
            print("Invalid delivery schedule.\n")
            return

        cursor.execute(
            """
            UPDATE suppliers
            SET
                supplier_name = ?,
                contact_number = ?,
                email_address = ?,
                delivery_schedule = ?
            WHERE supplier_id = ?
            """,
            (
                new_name,
                new_contact_number,
                new_email_address,
                new_delivery_schedule,
                supplier_id
            )
        )

        conn.commit()

        print("Supplier updated successfully!\n")

    finally:
        conn.close()

# DELETE 
def delete_supplier():

    if not view_supplier():
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        try:
            supplier_id = int(
                input("Enter supplier ID to delete: ")
            )

        except ValueError:
            print("Invalid supplier ID.\n")
            return

        cursor.execute(
            """
            DELETE FROM suppliers
            WHERE supplier_id = ?
            """,
            (supplier_id,)
        )

        conn.commit()

        if cursor.rowcount > 0:
            print("Supplier deleted successfully!\n")
        else:
            print("Supplier not found.\n")

    finally:
        conn.close()
