from db import get_connection
from datetime import date
def add_book(title, author, genre):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    INSERT INTO books (title, author, genre, available)
    VALUES (%s, %s, %s, TRUE)
    """

    cur.execute(query, (title, author, genre))
    conn.commit()
    conn.close()
def get_books():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT book_id, title, author, genre, available 
        FROM books
    """)
    books = cur.fetchall()

    conn.close()
    return books
def issue_book(user_id, book_id):

    conn = get_connection()
    cur = conn.cursor()

    # 1. Check if book is already issued
    cur.execute("""
        SELECT available FROM books
        WHERE book_id = %s
    """, (book_id,))

    result = cur.fetchone()

    if not result:
        conn.close()
        return "Book not found"

    if result[0] is False:
        conn.close()
        return "Book already issued"

    # 2. Insert transaction
    cur.execute("""
    INSERT INTO transactions
    (user_id, book_id, issue_date, due_date, status)
    VALUES
    (
        %s,
        %s,
        CURRENT_DATE,
        CURRENT_DATE + INTERVAL '14 days',
        'issued'
    )
    """, (user_id, book_id))

    # 3. Update book availability
    cur.execute("""
        UPDATE books
        SET available = FALSE
        WHERE book_id = %s
    """, (book_id,))

    conn.commit()
    conn.close()

    return "success"

def return_book(transaction_id, book_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE transactions
        SET
            status='returned',
            return_date=CURRENT_DATE
        WHERE transaction_id=%s
    """, (transaction_id,))

    cur.execute("""
        UPDATE books
        SET available=TRUE
        WHERE book_id=%s
    """, (book_id,))

    conn.commit()
    conn.close()

    fine = calculate_fine(book[0])

    if fine > 0:
        st.error(f"Fine to be collected: ₹{fine}")
    else:
        st.success("No fine.")
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

    query = """
    SELECT *
    FROM books
    WHERE
        title ILIKE %s OR
        author ILIKE %s OR
        genre ILIKE %s
    """

    value = f"%{keyword}%"

    cur.execute(query, (value, value, value))

    books = cur.fetchall()

    conn.close()

    return books
def update_book(book_id, title, author, genre):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    UPDATE books
    SET title=%s,
        author=%s,
        genre=%s
    WHERE book_id=%s
    """

    cur.execute(query, (title, author, genre, book_id))

    conn.commit()
    conn.close()

def delete_book(book_id):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    DELETE FROM books
    WHERE book_id=%s
    """

    cur.execute(query, (book_id,))

    conn.commit()
    conn.close()

def get_borrowed_books(user_id):

        conn = get_connection()
        cur = conn.cursor()

        query = """
        SELECT
            books.title,
            books.author,
            transactions.issue_date,
            transactions.return_date,
            transactions.status

        FROM transactions

        JOIN books
        ON books.book_id = transactions.book_id

        WHERE transactions.user_id = %s
        """

        cur.execute(query, (user_id,))

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


def calculate_fine(transaction_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT due_date
        FROM transactions
        WHERE transaction_id = %s
    """, (transaction_id,))

    result = cur.fetchone()

    if not result:
        conn.close()
        return 0

    due_date = result[0]

    from datetime import date

    today = date.today()

    overdue_days = (today - due_date).days

    conn.close()

    if overdue_days > 0:
        return overdue_days * 10

    return 0