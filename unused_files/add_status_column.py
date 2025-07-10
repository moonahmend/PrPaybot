import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

# Check if 'status' column exists
c.execute("PRAGMA table_info(orders)")
columns = [row[1] for row in c.fetchall()]

if 'status' not in columns:
    c.execute("ALTER TABLE orders ADD COLUMN status TEXT DEFAULT 'completed'")
    print("'status' column added to 'orders' table.")
else:
    print("'status' column already exists in 'orders' table.")

conn.commit()
conn.close() 