import sqlite3

# This will create employee.db in the same folder
conn = sqlite3.connect("employee.db")
cursor = conn.cursor()

# Create departments table
cursor.execute("""
CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT
);
""")

# Create employees table
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_name TEXT NOT NULL,
    age INTEGER,
    salary INTEGER,
    join_date TEXT,
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);
""")

conn.commit()
conn.close()

print("employee.db created with tables")