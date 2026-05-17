import re

with open("main.py", "r") as f:
    content = f.read()

# 1. Replace import
content = content.replace("import mysql.connector", "import sqlite3")

# 2. Replace get_db_connection
old_conn = """def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Change to your MySQL user
        password="",  # Change to your MySQL password
        database="stego_db"
    )"""

new_conn = """def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shared_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            file_name TEXT,
            ecc_key TEXT,
            lsb_key TEXT,
            status TEXT DEFAULT 'Sent',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            secret_text TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()"""

content = content.replace(old_conn, new_conn)

# 3. Replace cursor(dictionary=True) -> cursor()
content = content.replace("cursor(dictionary=True)", "cursor()")

# 4. Replace %s with ?
# We can do a regex replace for %s inside execute statements, but %s is also used in string formatting.
# Luckily, looking at the code, execute(..., (var1, var2)) is how %s is used.
# But python's string format f"Registration Success!" doesn't use %s.
# Let's replace "%s" with "?" for execute statements carefully.
# We will just replace `%s` with `?` in the specific lines/blocks that are SQL queries.
sql_blocks = [
    ("VALUES (%s, %s, %s, %s, %s, %s, %s)", "VALUES (?, ?, ?, ?, ?, ?, ?)"),
    ("email = %s AND password = %s", "email = ? AND password = ?"),
    ("sender_id = %s", "sender_id = ?"),
    ("receiver_id = %s", "receiver_id = ?"),
    ("id = %s", "id = ?"),
    ("id != %s", "id != ?"),
]

for old, new in sql_blocks:
    content = content.replace(old, new)

# 5. Add init_db() call before app.run()
old_run = """if __name__ == '__main__':
    # Ensure upload folder exists
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    app.run(debug=True)"""

new_run = """if __name__ == '__main__':
    # Ensure upload folder exists
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    init_db()  # Initialize the database
    app.run(debug=True)"""

content = content.replace(old_run, new_run)

with open("main.py", "w") as f:
    f.write(content)

print("Migration successful.")
