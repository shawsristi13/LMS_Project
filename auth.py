import bcrypt
from db import get_connection

# ---------------- PASSWORD HASH ----------------
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# ---------------- PASSWORD CHECK ----------------
def check_password(password, hashed_password):
    return bcrypt.checkpw(
        password.encode(),
        hashed_password.encode()
    )

# ---------------- LOGIN USER ----------------
def login_user(email, password, role):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT user_id, name, email, password, role
        FROM users
        WHERE email=%s AND role=%s
    """, (email, role))

    user = cur.fetchone()
    conn.close()

    print("USER FROM DB:", user)

    if user:
        print("PASSWORD MATCH:", check_password(password, user[3]))

    if user and check_password(password, user[3]):
        return user

    return None