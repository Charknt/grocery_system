# reports.py

from db import get_connection


# SALES SUMMARY
def sales_summary():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(total_amount), 0)
            FROM sales
        """)

        total_transactions, total_sales = cursor.fetchone()

        print("\n=== SALES SUMMARY ===")
        print(f"Total Transactions: {total_transactions}")
        print(f"Total Sales Amount: ₱{total_sales:.2f}\n")

    finally:
        conn.close()


# DELIVERY SUMMARY
def delivery_summary():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(total_cost), 0)
            FROM deliveries
        """)

        total_deliveries, total_cost = cursor.fetchone()

        print("\n=== DELIVERY SUMMARY ===")
        print(f"Total Deliveries: {total_deliveries}")
        print(f"Total Delivery Cost: ₱{total_cost:.2f}\n")

    finally:
        conn.close()


# INVENTORY SUMMARY
def inventory_summary():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                product_name,
                stock_quantity,
                unit_price
            FROM products
            ORDER BY product_name
        """)

        products = cursor.fetchall()

        if not products:
            print("No products found.\n")
            return

        print("\n=== INVENTORY SUMMARY ===")

        for product in products:

            stock_value = (
                product[1] * product[2]
            )

            print(
                f"\nProduct: {product[0]}"
                f"\nStock: {product[1]}"
                f"\nUnit Price: ₱{product[2]:.2f}"
                f"\nStock Value: ₱{stock_value:.2f}"
            )

        print()

    finally:
        conn.close()


# BEST SELLING PRODUCT
def best_selling_product():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                p.product_name,
                SUM(s.quantity_sold) AS total_sold
            FROM sales s
            JOIN products p
                ON s.product_id = p.product_id
            GROUP BY p.product_name
            ORDER BY total_sold DESC
            LIMIT 1
        """)

        result = cursor.fetchone()

        if not result:
            print("No sales records found.\n")
            return

        print("\n=== BEST SELLING PRODUCT ===")
        print(f"Product: {result[0]}")
        print(f"Total Quantity Sold: {result[1]}\n")

    finally:
        conn.close()

def low_stock_report():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                product_name,
                stock_quantity
            FROM products
            WHERE stock_quantity <= 10
            ORDER BY stock_quantity
        """)

        products = cursor.fetchall()

        if not products:
            print("No low stock products found.\n")
            return

        print("\n=== LOW STOCK REPORT ===")

        for product in products:

            print(
                f"\nProduct: {product[0]}"
                f"\nRemaining Stock: {product[1]}"
            )

        print()

    finally:
        conn.close()
