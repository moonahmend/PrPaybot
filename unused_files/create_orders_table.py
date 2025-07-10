import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER,
    order_type TEXT,
    details TEXT,
    amount INTEGER,
    created_at TEXT,
    status TEXT DEFAULT 'completed'
)
''')
conn.commit()
conn.close()
print("orders table created (if not exists).")
