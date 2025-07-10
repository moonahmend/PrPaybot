import sqlite3

# Connect to the database
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Check if 'middle_name' column exists
c.execute("PRAGMA table_info(customer_profiles)")
columns = [col[1] for col in c.fetchall()]

if 'middle_name' not in columns:
    c.execute("ALTER TABLE customer_profiles ADD COLUMN middle_name TEXT;")
    print("'middle_name' column added to customer_profiles table.")
else:
    print("'middle_name' column already exists.")

conn.commit()
conn.close() 