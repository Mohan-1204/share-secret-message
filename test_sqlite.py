import sqlite3

conn = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES)
cursor = conn.cursor()
cursor.execute('CREATE TABLE test (id INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
cursor.execute('INSERT INTO test (id) VALUES (1)')
cursor.execute('SELECT * FROM test')
row = cursor.fetchone()
print(type(row[1]))
print(row[1])
