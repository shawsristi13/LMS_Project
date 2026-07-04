from db import get_connection
from auth import hash_password

def add_user(name, email, password, role):

    conn = get_connection()
    cur = conn.cursor()

    # check duplicate email
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    if cur.fetchone():
        conn.close()
        return "exists"

    hashed_pw = hash_password(password)

    cur.execute("""
        INSERT INTO users (name, email, password, role)
        VALUES (%s, %s, %s, %s)
    """, (name, email, hashed_pw, role))

    conn.commit()
    conn.close()

    return "success"


def get_students():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, name
        FROM users
        WHERE role='student'
        ORDER BY name
    """)

    students = cur.fetchall()

    conn.close()

    return students