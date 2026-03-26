import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "blood.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create donors table
cursor.execute("""
CREATE TABLE donors (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
blood_group TEXT,
phone TEXT,
email TEXT,
city TEXT,
age INTEGER,
last_donated TEXT,
units INTEGER,
availability TEXT,
username TEXT,
password TEXT
)
""")

conn.commit()
conn.close()

print("Database and donors table created successfully at:", db_path)