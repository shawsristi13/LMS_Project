import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host="ep-frosty-flower-adgt9763.c-2.us-east-1.aws.neon.tech",
        database="neondb",
        user="neondb_owner",
        password="npg_GWrvY6NbelX5",
        port="5432",
        sslmode="require"
    )
    return conn