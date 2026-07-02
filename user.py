from db import get_connection

def add_user(name, email, password, role):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    INSERT INTO users(name, email, password, role)
    VALUES (%s, %s, %s, %s)
    """

    cur.execute(query, (name, email, password, role))

    conn.commit()
    conn.close()


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