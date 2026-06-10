from db import get_connection

ROLES = [
    "cashier",
    "stocker",
    "janitor",
    "manager"
]

SHIFTS = [
    "morning (6AM - 2PM)",
    "afternoon (2PM - 10PM)",
    "night (10PM - 6AM)",
    "full day (8AM - 5PM)"
]

# CREATE
def add_staff():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        first_name = input("Enter first name: ").strip()

        if not first_name:
            print("First name cannot be empty.\n")
            return
        
        if not first_name.replace(" ", "").isalpha():
            print("Invalid first name.\n")
            return
        
        while True:
            middle_initial = input("Enter middle initial (Press Enter to skip): ").strip()

            if not middle_initial:
                middle_initial = None
                break

            if len(middle_initial) == 1 and middle_initial.isalpha():
                middle_initial = middle_initial.upper()
                break

            print("Invalid input. Please enter only one letter.")

        last_name = input("Enter last name: ").strip()

        if not last_name:
            print("Last name cannot be empty.\n")
            return

        if not last_name.replace(" ", "").isalpha():
            print("Invalid last name.\n")
            return
        
        print("\nAvailable Roles:")

        for i, role in enumerate(ROLES, start=1):
            print(f"{i}. {role}")

        try:
            role_choice = int(input("Choose role: "))
            selected_role = ROLES[role_choice - 1]

        except (ValueError, IndexError):
            print("Invalid role selection.\n")
            return

        print("\nAvailable Shifts:")

        for i, shift in enumerate(SHIFTS, start=1):
            print(f"{i}. {shift}")

        try:
            shift_choice = int(input("Choose shift: "))
            selected_shift = SHIFTS[shift_choice - 1]

        except (ValueError, IndexError):
            print("Invalid shift selection.\n")
            return

        contact_number = input("Enter contact number: ").strip()

        if not contact_number:
            print("Contact number cannot be empty.\n")
            return
        
        if not contact_number.isdigit() or len(contact_number) != 11:
            print("Invalid contact number.\n")
            return
        
        cursor.execute(
            """
            INSERT INTO staffs(
                first_name,
                middle_initial,
                last_name,
                role,
                shift,
                contact_number
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                first_name, 
                middle_initial, 
                last_name, 
                selected_role, 
                selected_shift, 
                contact_number
            )
        )

        conn.commit()
        print("Staff member added successfully!\n")

    finally:
        conn.close()


# READ
def view_staff():

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM staffs")

        staff_members = cursor.fetchall()

        if not staff_members:
            print("There are no staff members. Please add staff first.\n")
            return False

        print("\n=== STAFF LIST ===")

        for member in staff_members:
            mi = f" {member[2]}." if member[2] else ""
            full_name = f"{member[1]}{mi} {member[3]}"
            print(
                f"{member[0]}. Name: {full_name} | "
                f"Role: {member[4]} | "
                f"Shift: {member[5]} | "
                f"Contact: {member[6]}"
            )
        print()
        return True

    finally:
        conn.close()


# UPDATE
def update_staff():

    if not view_staff():
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        try:
            staff_id = int(input("Enter staff ID to update: "))

        except ValueError:
            print("Invalid staff ID.\n")
            return

        cursor.execute(
            """
            SELECT * FROM staffs
            WHERE staff_id = ?
            """,
            (staff_id,)
        )

        if not cursor.fetchone():
            print("Staff member not found.\n")
            return

        new_first_name = input("New first name: ").strip()

        if not new_first_name:
            print("First name cannot be empty.\n")
            return

        if not new_first_name.replace(" ", "").isalpha():
            print("Invalid first name.\n")
            return
        
        while True:
            new_middle_initial = input("New middle initial (Press Enter to skip): ").strip()

            if not new_middle_initial:
                new_middle_initial = None
                break

            if len(new_middle_initial) == 1 and new_middle_initial.isalpha():
                new_middle_initial = new_middle_initial.upper()
                break
                
            if new_middle_initial.isdigit():
                print("Invalid Input.\n")

        new_last_name = input("New last name: ").strip()

        if not new_last_name:
            print("Last name cannot be empty.\n")
            return

        if not new_last_name.replace(" ", "").isalpha():
            print("Invalid last name.\n")
            return
        
        print("\nAvailable Roles:")

        for i, role in enumerate(ROLES, start=1):
            print(f"{i}. {role}")

        try:
            role_choice = int(input("Choose new role: "))
            new_role = ROLES[role_choice - 1]

        except (ValueError, IndexError):
            print("Invalid role selection.\n")
            return

        print("\nAvailable Shifts:")

        for i, shift in enumerate(SHIFTS, start=1):
            print(f"{i}. {shift}")

        try:
            shift_choice = int(input("Choose new shift: "))
            new_shift = SHIFTS[shift_choice - 1]

        except (ValueError, IndexError):
            print("Invalid shift selection.\n")
            return

        new_contact_number = input("New contact number: ").strip()

        if not new_contact_number:
            print("Contact number cannot be empty.\n")
            return

        if not new_contact_number.isdigit() or len(new_contact_number) != 11:
            print("Invalid contact number.\n")
            return
        
        cursor.execute(
            """
            UPDATE staffs
            SET
                first_name = ?,
                middle_initial = ?,
                last_name = ?,
                role = ?,
                shift = ?,
                contact_number = ?
            WHERE staff_id = ?
            """,
            (
                new_first_name,
                new_middle_initial,
                new_last_name,
                new_role,
                new_shift,
                new_contact_number,
                staff_id
            )
        )

        conn.commit()
        print("Staff member updated successfully!\n")

    finally:
        conn.close()


# DELETE
def delete_staff():
    
    if not view_staff():
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        
        try:
            staff_id = int(input("Enter staff ID to delete: "))

        except ValueError:
            print("Invalid staff ID.\n")
            return
        
        cursor.execute(
            """
            SELECT *
            FROM deliveries
            WHERE staff_id = ?
            """,
            (staff_id,)
        )

        if cursor.fetchone():
            print(
                "Cannot delete staff. "
                "\nStaff is used in delivery records."
            )
            return
        
        cursor.execute(
            """
            SELECT *
            FROM sales
            WHERE staff_id = ?
            """,
            (staff_id,)
        )

        if cursor.fetchone():
            print(
                "Cannot delete staff. "
                "\nStaff is used in sales records."
            )
            return
        
        cursor.execute(
            """
            DELETE FROM staffs
            WHERE staff_id = ?
            """,
            (staff_id,)
        )

        conn.commit()

        if cursor.rowcount > 0:
            print("Staff member deleted successfully!\n")
        else:
            print("Staff member not found.\n")

    finally:
        conn.close()


# SEARCH
def search_staff():

    keyword = input("Enter staff name to search: ").strip()

    if not keyword:
        print("Search keyword cannot be empty.\n")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM staffs
            WHERE LOWER(first_name)
                LIKE LOWER(?)
            OR LOWER(last_name)
                LIKE LOWER(?)
            """,
            (
                f"%{keyword}%",
                f"%{keyword}%"
            )
        )

        staffs = cursor.fetchall()

        if not staffs:
            print("No staff found.\n")
            return

        print("\n=== SEARCH RESULT ===")

        for staff in staffs:

            mi = (
                f" {staff[2]}."
                if staff[2]
                else ""
            )

            print(
                f"{staff[0]} | "
                f"{staff[1]}{mi} {staff[3]} | "
                f"Role: {staff[4]} | "
                f"Shift: {staff[5]} | "
                f"Contact: {staff[6]}"
            )

        print()

    finally:
        conn.close()

