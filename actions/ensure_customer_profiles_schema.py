import sqlite3

DB_PATH = 'users.db'

REQUIRED_COLUMNS = [
    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
    ("telegram_id", "INTEGER"),
    ("profile_number", "INTEGER"),
    ("first_name", "TEXT"),
    ("middle_name", "TEXT"),
    ("last_name", "TEXT"),
    ("email", "TEXT"),
    ("phone_number", "TEXT"),
    ("address_line_1", "TEXT"),
    ("address_line_2", "TEXT"),
    ("city", "TEXT"),
    ("state", "TEXT"),
    ("postal_code", "TEXT"),
    ("country", "TEXT"),
    ("date_of_birth", "TEXT"),
    ("gender", "TEXT"),
    ("identification_number", "TEXT"),
    ("preferred_contact_method", "TEXT"),
    ("password", "TEXT"),
    ("profile_id", "TEXT"),
    ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
]

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create table if not exists with only the required columns that are not already present
    c.execute(f"""
    CREATE TABLE IF NOT EXISTS customer_profiles (
        {', '.join([f'{col} {coltype}' for col, coltype in REQUIRED_COLUMNS])}
    )
    """)
    # Add any missing columns
    for col, coltype in REQUIRED_COLUMNS:
        if not column_exists(c, 'customer_profiles', col):
            print(f"Adding column: {col}")
            c.execute(f"ALTER TABLE customer_profiles ADD COLUMN {col} {coltype}")
        else:
            print(f"Column already exists: {col}")
    conn.commit()
    conn.close()
    print("Schema check complete.")

if __name__ == '__main__':
    main() 