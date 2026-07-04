from auth import hash_password
from db import get_connection

conn = get_connection()
cur = conn.cursor()

hashed = hash_password("admin123")

cur.execute("""
INSERT INTO users (name, email, password, role)
VALUES (%s, %s, %s, %s)
""", (
    "Admin User",
    "admin@gmail.com",
    hashed,
    "admin"
))

conn.commit()
conn.close()

print("Admin created successfully!")