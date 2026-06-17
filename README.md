# Grocery Inventory and Sales Management System

A beginner-friendly Python desktop application that manages grocery products, suppliers, staff members, deliveries, sales transactions, and reports using a SQLite database.

## Project Information

* **Topic:** Inventory and Sales Management
* **Level:** Intermediate
* **Programming Language:** Python
* **Database:** SQLite
* **Interface:** Tkinter Desktop GUI

## Project Description

The Grocery Inventory and Sales Management System is a desktop application designed to help grocery stores organize and manage their daily operations.

The system allows users to manage products, suppliers, staff members, deliveries, and sales through an easy-to-use graphical user interface. It automatically updates inventory levels whenever deliveries are received or sales transactions are recorded.

All records are stored in a SQLite database, ensuring that information remains organized and persistent between program sessions.

## Learning Objectives

This project demonstrates how to:

* Build a desktop application using Tkinter
* Create graphical user interfaces using frames, buttons, labels, and tables
* Connect Python applications to a SQLite database
* Implement CRUD (Create, Read, Update, Delete) operations
* Apply input validation and error handling
* Manage inventory stock automatically
* Generate summary reports from stored data
* Organize large programs using modular programming

## Dashboard Features

### Product Management

* Add Product
* View Products
* Update Product
* Delete Product
* Search Product

### Supplier Management

* Add Supplier
* View Suppliers
* Update Supplier
* Delete Supplier
* Search Supplier

### Staff Management

* Add Staff Member
* View Staff Members
* Update Staff Member
* Delete Staff Member
* Search Staff Member

### Delivery Management

* Record Deliveries
* View Delivery Records
* Update Delivery Records
* Delete Delivery Records

### Sales Management

* Record Sales
* View Sales Records
* Update Sales Records
* Delete Sales Records
* Search Sales Records

### Reports Dashboard

* Sales Summary
* Delivery Summary
* Inventory Summary
* Best Selling Product

## Database Structure

The system uses five relational database tables:

### Products

Stores:

* Product Name
* Category
* Brand
* Unit Price
* Stock Quantity
* Expiry Date

### Suppliers

Stores:

* Supplier Name
* Contact Number
* Email Address
* Delivery Schedule

### Staffs

Stores:

* First Name
* Middle Initial
* Last Name
* Role
* Shift
* Contact Number

### Deliveries

Stores:

* Delivery Date
* Quantity Received
* Total Cost
* Supplier Reference
* Product Reference
* Staff Reference

### Sales

Stores:

* Sale Date
* Quantity Sold
* Total Amount
* Product Reference
* Staff Reference

## GUI Features

The Tkinter interface provides:

* Navigation buttons
* Data entry forms
* Validation messages
* Search functionality
* Report viewing
* Organized management screens
* User-friendly workflow

## Libraries Used

* Tkinter
* SQLite3
* Datetime

## Project Structure

```text
Grocery Inventory and Sales Management System/

├── main.py
├── db.py
├── product.py
├── supplier.py
├── staff.py
├── delivery.py
├── sales.py
├── reports.py
├── grocery.db
└── README.md
```

## Installation

Make sure Python 3 is installed.

No external libraries are required.

Tkinter is included with most Python installations.

## How to Run

Open a terminal inside the project folder and run:

```bash
python main.py
```

or

```bash
py main.py
```

## Expected Output

After launching the application, users can:

1. Manage grocery products
2. Manage suppliers
3. Manage staff records
4. Record deliveries
5. Record sales
6. Automatically update inventory stock
7. Search records quickly
8. Generate summary reports
9. Interact with the system through a graphical user interface

## Data Integrity Rules

The system enforces the following rules:

* Product names must be unique
* Supplier names must be unique
* Prices must be greater than zero
* Quantities cannot be negative
* Sales cannot exceed available stock
* Stock cannot become negative
* Products linked to sales or deliveries cannot be deleted
* Suppliers linked to deliveries cannot be deleted
* Staff linked to sales or deliveries cannot be deleted

## Entry Point

```python
if __name__ == "__main__":
    main()
```
