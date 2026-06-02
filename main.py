from product import (
    add_product,
    view_products,
    update_product,
    delete_product
)

from supplier import (
    add_supplier,
    view_supplier,
    update_supplier,
    delete_supplier
)

while True:

    print("=== GROCERY INVENTORY SYSTEM ===")
    print("1. Add Product")
    print("2. View Products")
    print("3. Update Product")
    print("4. Delete Product")
    print("5. Add Supplier")
    print("6. View Supplier")
    print("7. Update Supplier")
    print("8. Delete Supplier")
    print("9. Exit")

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
        add_supplier()

    elif choice == "6":
        view_supplier()

    elif choice == "7":
        update_supplier()

    elif choice == "8":
        delete_supplier()
    
    elif choice == "9":
        print("Thank you for using the system!")
        break
    else:
        print("Invalid choice.\n")
