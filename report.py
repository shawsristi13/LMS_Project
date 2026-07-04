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

        data.append({
            "Book ID": book[0],
            "Title": book[1],
            "Author": book[2],
            "Genre": book[3],
            "ISBN": book[4],
            "Publisher": book[5],
            "Year": book[6],
            "Total Copies": book[7],
            "Available": "Yes" if book[8] else "No",
            "Shelf": book[9]
        })

    filename = "books_report.xlsx"

    wb.save(filename)

    return filename