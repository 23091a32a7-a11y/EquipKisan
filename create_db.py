import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
email TEXT NOT NULL UNIQUE,
password TEXT NOT NULL
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS equipment(
equipment_no TEXT,
equipment_name TEXT,
owner_name TEXT,
availability TEXT,
district TEXT,
phone TEXT,
rent INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS bookings(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
user_email TEXT,
equipment_name TEXT,
owner_name TEXT,
district TEXT,
phone TEXT,
rent INTEGER,
payment_method TEXT,
booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()

print("Database Created with UNIQUE email & bookings table")