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

from staff import (
    add_staff,
    view_staff,
    update_staff,
    delete_staff
)

from delivery import (
     add_delivery,
     view_delivery,
     update_delivery,
     delete_delivery
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
    print("9. Add Staff")
    print("10. View Staff")
    print("11. Update Staff")
    print("12. Delete Staff")    
    print("13. Add Delivery")
    print("14. View Delivery")
    print("15. Update Delivery")
    print("16. Delete Delivery")
    print("17. Exit")

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
        add_staff()

    elif choice == "10":
        view_staff()

    elif choice == "11":
        update_staff()

    elif choice == "12":
        delete_staff()

    elif choice == "13":
        add_delivery()

    elif choice == "14":
        view_delivery()

    elif choice == "15":
        update_delivery()

    elif choice == "16":
        delete_delivery()

    elif choice == "17":
        print("Thank you for using the system!")
        break
        
    else:
        print("Invalid choice.\n")
