from db import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("SELECT version();")
db_version = cur.fetchone()

print("Connected to:", db_version)

conn.close()