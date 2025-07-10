import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute("PRAGMA table_info(customer_profiles);")
columns = c.fetchall()
print("customer_profiles table columns:")
for col in columns:
    print(col)
conn.close() 