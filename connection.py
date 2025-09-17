import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to MySQL server (without specifying database)
cnx = mysql.connector.connect(
    host=os.getenv("HOST"),
    port=os.getenv("PORT"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD")
)

cur = cnx.cursor()

# Create database if it doesn't exist
cur.execute("CREATE DATABASE IF NOT EXISTS employee_erp")
cnx.commit()

# Close initial connection and reconnect to the database
cnx.close()

# Connect to the employee_erp database
cnx = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="Root",
    database="employee_erp"
)

cur = cnx.cursor()

def table_exists(table_name):
    cur.execute("SHOW TABLES LIKE %s", (table_name,))
    return cur.fetchone() is not None

def create_table():
    # Check and create departments table
    if not table_exists('departments'):
        cur.execute("""
        CREATE TABLE departments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE
        )
        """)
        print("Created departments table")
    else:
        print("Departments table already exists")

    # Check and create roles table
    if not table_exists('roles'):
        cur.execute("""
        CREATE TABLE roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            level INT NOT NULL
        )
        """)
        print("Created roles table")
    else:
        print("Roles table already exists")

    # Check and create employees table
    if not table_exists('employees'):
        cur.execute("""
        CREATE TABLE employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            department_id INT,
            role_id INT,
            salary DECIMAL(10,2),
            hire_date DATE,
            FOREIGN KEY (department_id) REFERENCES departments(id),
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )
        """)
        print("Created employees table")
    else:
        print("Employees table already exists")

    cnx.commit()

# Insert default departments if not exist
    cur.execute("INSERT IGNORE INTO departments (name) VALUES ('HR'), ('IT'), ('Finance'), ('Marketing')")
    cnx.commit()

# Insert default roles if not exist
    cur.execute("INSERT IGNORE INTO roles (name, level) VALUES ('Intern', 1), ('Analyst', 2), ('Developer', 3), ('Manager', 4)")
    cnx.commit()

# Call the function to create tables if they don't exist
create_table()

print("Database and tables set up successfully.")
