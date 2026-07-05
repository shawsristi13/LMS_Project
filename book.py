from db import get_connection
from datetime import date

def calculate_fine(transaction_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT due_date, return_date
        FROM transactions
        WHERE transaction_id = %s
    """, (transaction_id,))

    data = cur.fetchone()
    conn.close()

    if not data:
        return 0

    due_date, return_date = data

    # if not returned yet, use today
    if return_date:
        end_date = return_date
    else:
        end_date = date.today()

    overdue_days = (end_date - due_date).days

    if overdue_days > 0:
        return overdue_days * 10   # ₹10 per day fine

    return 0
def add_book(
    title,
    author,
    genre,
    isbn,
    publisher,
    publication_year,
    total_copies,
    shelf_no
):

    conn = get_connection()
    cur = conn.cursor()

    query = """
    INSERT INTO books
    (
        title,
        author,
        genre,
        isbn,
        publisher,
        publication_year,
        total_copies,
        available_copies,
        shelf_no
    )
    VALUES
    (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cur.execute(
        query,
        (
            title,
            author,
            genre,
            isbn,
            publisher,
            publication_year,
            total_copies,
            total_copies,
            shelf_no
        )
    )

    conn.commit()
    conn.close()
def get_books():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            book_id,
            title,
            author,
            genre,
            isbn,
            publisher,
            publication_year,
            total_copies,
            available,
            shelf_no
        FROM books
        ORDER BY title
    """)

    books = cur.fetchall()
    conn.close()
    return books

def return_book(transaction_id, book_id):

    conn = get_connection()
    cur = conn.cursor()

    fine = calculate_fine(transaction_id)

    cur.execute("""
        UPDATE transactions
        SET status = 'returned',
            return_date = CURRENT_DATE,
            fine = %s
        WHERE transaction_id = %s
    """, (fine, transaction_id))

    cur.execute("""
        UPDATE books
        SET available = TRUE
        WHERE book_id = %s
    """, (book_id,))

    conn.commit()
    conn.close()

    return fine

def get_available_books():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT book_id, title FROM books WHERE available = TRUE
    """)
    books = cur.fetchall()

    conn.close()
    return books
def search_books(keyword):
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
        WHERE
            title ILIKE %s OR
            author ILIKE %s OR
            genre ILIKE %s
        ORDER BY title
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))

    books = cur.fetchall()
    conn.close()
    return books
def update_book(book_id, title, author, genre):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE books
        SET title=%s,
            author=%s,
            genre=%s
        WHERE book_id=%s
    """, (title, author, genre, book_id))

    conn.commit()
    conn.close()

def delete_book(book_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM books
        WHERE book_id=%s
    """, (book_id,))

    conn.commit()
    conn.close()
def get_borrowed_books(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            b.title,
            b.author,
            t.issue_date,
            t.due_date,
            t.return_date,
            t.status
        FROM transactions t
        JOIN books b
        ON b.book_id = t.book_id
        WHERE t.user_id = %s
        ORDER BY t.issue_date DESC
    """, (user_id,))

    books = cur.fetchall()
    conn.close()

    return books
def get_available_books():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT book_id, title
        FROM books
        WHERE available = TRUE
        ORDER BY title
    """)

    books = cur.fetchall()

    conn.close()

    return books


def issue_book(user_id, book_id):

    conn = get_connection()
    cur = conn.cursor()

    # check availability
    cur.execute("""
        SELECT available
        FROM books
        WHERE book_id=%s
    """, (book_id,))

    result = cur.fetchone()

    if not result or result[0] is False:
        conn.close()
        return "Book not available"

    cur.execute("""
        INSERT INTO transactions (
            user_id,
            book_id,
            issue_date,
            due_date,
            status
        )
        VALUES (
            %s,
            %s,
            CURRENT_DATE,
            CURRENT_DATE + INTERVAL '14 days',
            'issued'
        )
    """, (user_id, book_id))

    cur.execute("""
        UPDATE books
        SET available = FALSE
        WHERE book_id=%s
    """, (book_id,))

    conn.commit()
    conn.close()

    return "success"

def get_issued_books(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            t.transaction_id,
            b.book_id,
            b.title

        FROM transactions t

        JOIN books b
        ON t.book_id = b.book_id

        WHERE
            t.user_id = %s
            AND t.status = 'issued'

        ORDER BY b.title
    """, (user_id,))

    books = cur.fetchall()

    conn.close()

    return books

def get_overdue_books():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            u.name,
            b.title,
            t.issue_date,
            t.due_date,
            CURRENT_DATE - t.due_date AS overdue_days

        FROM transactions t

        JOIN users u
        ON t.user_id = u.user_id

        JOIN books b
        ON t.book_id = b.book_id

        WHERE
            t.status = 'issued'
            AND t.due_date < CURRENT_DATE

        ORDER BY overdue_days DESC
    """)

    books = cur.fetchall()

    conn.close()

    return books