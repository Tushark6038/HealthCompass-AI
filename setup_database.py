import sqlite3

# 1. Connect to database (or create it if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 2. Create the 'users' table
# This replaces the CSV header row
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        usage_count INTEGER DEFAULT 0
    )
''')

print("Database 'database.db' created successfully!")

# 3. Save and Close
conn.commit()
conn.close()