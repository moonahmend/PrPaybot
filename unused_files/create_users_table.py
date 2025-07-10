import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    balance INTEGER DEFAULT 0,
    welcomed INTEGER DEFAULT 0,
    subscription_active INTEGER DEFAULT 0
)
''')
conn.commit()
conn.close()
print("users table created (if not exists).")
