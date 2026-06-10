from product import (
    add_product,
    view_products,
    update_product,
    delete_product,
    search_product
)

from supplier import (
    add_supplier,
    view_supplier,
    update_supplier,
    delete_supplier,
    search_supplier
)

from staff import (
    add_staff,
    view_staff,
    update_staff,
    delete_staff,
    search_staff
)

from delivery import (
    add_delivery,
    view_delivery,
    update_delivery,
    delete_delivery,
    search_delivery
)

from sales import (
    add_sale,
    view_sales,
    update_sale,
    delete_sale,
    search_sale
)

from reports import (
    sales_summary,
    delivery_summary,
    inventory_summary,
    best_selling_product,
    low_stock_report
)


while True:

    print("=== GROCERY INVENTORY SYSTEM ===")
    print("1.  Add Product")
    print("2.  View Products")
    print("3.  Update Product")
    print("4.  Delete Product")
    print("5.  Search Product")

    print("6.  Add Supplier")
    print("7.  View Supplier")
    print("8.  Update Supplier")
    print("9.  Delete Supplier")
    print("10. Search Supplier")
    
    print("11. Add Staff")
    print("12. View Staff")
    print("13. Update Staff")
    print("14. Delete Staff")
    print("15. Search Staff")

    print("16. Add Delivery")
    print("17. View Delivery")
    print("18. Update Delivery")
    print("19. Delete Delivery")
    print("20. Search Delivery")

    print("21. Add Sale")
    print("22. View Sales")
    print("23. Update Sale")
    print("24. Delete Sale")
    print("25. Search Sale")

    print("26. Sales Summary")
    print("27. Delivery Summary")
    print("28. Inventory Summary")
    print("29. Best Selling Product")
    print("30. Low Stock Report")
    print("31. Exit")

    choice = input("\nChoose an option: ").strip()

    if choice == "1":
        add_product()

    elif choice == "2":
        view_products()

    elif choice == "3":
        update_product()

    elif choice == "4":
        delete_product()

    elif choice == "5":
        search_product()

    elif choice == "6":
        add_supplier()

    elif choice == "7":
        view_supplier()

    elif choice == "8":
        update_supplier()

    elif choice == "9":
        delete_supplier()

    elif choice == "10":
        search_supplier()

    elif choice == "11":
        add_staff()

    elif choice == "12":
        view_staff()

    elif choice == "13":
        update_staff()

    elif choice == "14":
        delete_staff()

    elif choice == "15":
        search_staff()

    elif choice == "16":
        add_delivery()

    elif choice == "17":
        view_delivery()

    elif choice == "18":
        update_delivery()

    elif choice == "19":
        delete_delivery()

    elif choice == "20":
        search_delivery()

    elif choice == "21":
        add_sale()

    elif choice == "22":
        view_sales()

    elif choice == "23":
        update_sale()

    elif choice == "24":
        delete_sale()

    elif choice == "25":
        search_sale()

    elif choice == "26":
        sales_summary()

    elif choice == "27":
        delivery_summary()

    elif choice == "28":
        inventory_summary()

    elif choice == "29":
        best_selling_product()

    elif choice == "30":
        low_stock_report()

    elif choice == "31":
        print("Thank you for using the system!")
        break
    
    else:
        print("Invalid choice.\n")
