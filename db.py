import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="lms_db",
        user="postgres",
        password="Iisc@2029",
        port="5432"
    )
    return conn