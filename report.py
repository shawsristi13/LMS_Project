from openpyxl import Workbook
from db import get_connection


def export_books_excel():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            book_id,
            title,
            author,
            genre,
            available
        FROM books
        ORDER BY book_id
    """)

    books = cur.fetchall()

    conn.close()

    wb = Workbook()
    ws = wb.active

    ws.title = "Books"

    ws.append([
        "Book ID",
        "Title",
        "Author",
        "Genre",
        "Available"
    ])

    for book in books:

        ws.append([
            book[0],
            book[1],
            book[2],
            book[3],
            "Yes" if book[4] else "No"
        ])

    filename = "books_report.xlsx"

    wb.save(filename)

    return filename