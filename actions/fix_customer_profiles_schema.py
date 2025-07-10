import sqlite3

DB_PATH = 'users.db'

ALTERS = [
    ("middle_name", "TEXT"),
    ("password", "TEXT"),
    ("profile_id", "TEXT"),
]

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for col, coltype in ALTERS:
        if not column_exists(c, 'customer_profiles', col):
            print(f"Adding column: {col}")
            c.execute(f"ALTER TABLE customer_profiles ADD COLUMN {col} {coltype}")
        else:
            print(f"Column already exists: {col}")
    conn.commit()
    conn.close()
    print("Schema update complete.")

if __name__ == '__main__':
    main() 