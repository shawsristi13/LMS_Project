from db import get_connection

def login_user(email, password, role):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT * FROM users 
    WHERE email=%s AND password=%s AND role=%s
    """

    cur.execute(query, (email, password, role))
    user = cur.fetchone()

    conn.close()
    return user