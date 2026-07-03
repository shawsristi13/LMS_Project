import streamlit as st

from db import get_connection
from book import (
    add_book,
    get_books,
    issue_book,
    return_book,
    search_books,
    update_book,
    delete_book,
    get_borrowed_books,
    get_issued_books,
    calculate_fine
)
from auth import login_user
from user import add_user
from user import add_user, get_students
from book import get_available_books
import plotly.express as px
import pandas as pd
from report import export_books_excel
def load_css():

    with open("assets/style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css()


# ---------------- SESSION INIT ----------------

if "user" not in st.session_state:
    st.session_state["user"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None


# ---------------- TITLE ----------------

from config import APP_NAME

st.title(APP_NAME)

# ==========================================================
# LOGIN PAGE
# ==========================================================

if st.session_state["user"] is None:

    st.subheader("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["admin", "student"])

    if st.button("Login"):

        user = login_user(email, password, role)

        if user:
            st.session_state["user"] = user
            st.session_state["role"] = role
            st.success("Login Successful")

        else:
            st.error("Invalid Credentials")


# ==========================================================
# AFTER LOGIN
# ==========================================================

else:

    st.sidebar.success(f"Logged in as {st.session_state['role']}")

    # ---------------- MENU ----------------

    if st.session_state["role"] == "admin":

        menu = [
            "Dashboard",
            "User Management",
            "Add Book",
            "View Books",
            "Search Books",
            "Edit Book",
            "Delete Book",
            "Issue Book",
            "Return Book",
            "Reports",
            "Logout"
        ]
        choice = st.sidebar.selectbox("Menu", menu)

    else:

        menu = [
            "Dashboard",
            "View Books",
            "Search Books",
            "My Borrowed Books",
            "Logout"
        ]

    st.markdown("## 👇 Select an option from sidebar")

    st.success(
        f"Welcome back! Logged in as **{st.session_state['role'].capitalize()}**"
    )

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    if choice == "Dashboard":

        st.subheader("📊 Dashboard")

        col1, col2, col3, col4 = st.columns(4)

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM books")
        total_books = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM books WHERE available = TRUE")
        available_books = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM transactions WHERE status='issued'"
        )
        issued_books = cur.fetchone()[0]

        conn.close()

        col1.metric("📚 Total Books", total_books)
        col2.metric("👤 Total Users", total_users)
        col3.metric("📤 Issued Books", issued_books)
        col4.metric("✅ Available", available_books)

        st.divider()

        st.subheader("📚 Books by Genre")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT genre, COUNT(*)
        FROM books
        GROUP BY genre
        ORDER BY COUNT(*) DESC
        """)

        genre_data = cur.fetchall()

        conn.close()

        if genre_data:

            df = pd.DataFrame(
                genre_data,
                columns=["Genre", "Books"]
            )

            fig = px.bar(
                df,
                x="Genre",
                y="Books",
                title="Books Available by Genre"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        st.subheader("📖 Library Status")

        available = total_books - issued_books

        status_df = pd.DataFrame({
            "Status": ["Available", "Issued"],
            "Books": [available, issued_books]
        })

        fig = px.pie(
            status_df,
            names="Status",
            values="Books",
            hole=0.5,
            title="Book Availability"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ==========================================================
        # RECENTLY ADDED BOOKS
        # ==========================================================
        
        st.divider()

        st.subheader("📚 Recently Added Books")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT title, author, genre
        FROM books
        ORDER BY book_id DESC
        LIMIT 5
        """)

        recent_books = cur.fetchall()

        conn.close()

        if recent_books:
            st.table(recent_books)

    # ==========================================================
    # USER MANAGEMENT
    # ==========================================================

    elif choice == "User Management":

        st.subheader("👥 User Management")

        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        role = st.selectbox(
            "Select Role",
            ["student", "admin"]
        )

        if st.button("Create User"):

            add_user(name, email, password, role)

            st.success(f"{role.capitalize()} created successfully!")

    # ==========================================================
    # ADD BOOK
    # ==========================================================

    elif choice == "Add Book":

        st.subheader("➕ Add Book")

        title = st.text_input("Book Title")

        author = st.text_input("Author")

        genre = st.text_input("Genre")

        isbn = st.text_input("ISBN")

        publisher = st.text_input("Publisher")

        publication_year = st.number_input(
            "Publication Year",
            min_value=1900,
            max_value=2100,
            step=1
        )

        total_copies = st.number_input(
            "Total Copies",
            min_value=1,
            step=1
        )

        shelf_no = st.text_input("Shelf Number")

        if st.button("Add Book"):

            if title and author and genre:

                add_book(
                    title,
                    author,
                    genre,
                    isbn,
                    publisher,
                    publication_year,
                    total_copies,
                    shelf_no
                )

                st.success("Book added successfully!")

            else:

                st.warning("Please fill all fields.")

    # ==========================================================
    # VIEW BOOKS
    # ==========================================================

    elif choice == "View Books":

        st.subheader("📚 All Books")

        books = get_books()

        if books:

            data = []

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
                    "Available Copies": book[8],
                    "Shelf": book[9]
                })

            df = pd.DataFrame(data)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No books available.")

    # ==========================================================
    # SEARCH BOOK
    # ==========================================================

    elif choice == "Search Books":

        st.subheader("🔍 Search Books")

        keyword = st.text_input(
            "Search by Title, Author or Genre"
        )

        if keyword:

            books = search_books(keyword)

            if books:

                for book in books:

                    st.write(f"""
**📖 {book[1]}**

✍ Author : {book[2]}

📚 Genre : {book[3]}

Available : {"✅ Yes" if book[4] else "❌ No"}

---
""")

            else:

                st.warning("No matching books found.")

    # ==========================================================
    # BORROWED BOOKS
    # ==========================================================

    elif choice == "My Borrowed Books":

        st.subheader("📖 My Borrowed Books")

        user_id = st.session_state["user"][0]

        books = get_borrowed_books(user_id)

        if books:

            import pandas as pd

            df = pd.DataFrame(
                books,
                columns=[
                    "Title",
                    "Author",
                    "Issue Date",
                    "Return Date",
                    "Status"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("You have not borrowed any books.")

    # ==========================================================
    # EDIT BOOK
    # ==========================================================

    elif choice == "Edit Book":

        st.subheader("✏ Edit Book")

        book_id = st.number_input(
            "Book ID",
            min_value=1,
            step=1
        )

        title = st.text_input("New Title")
        author = st.text_input("New Author")
        genre = st.text_input("New Genre")

        if st.button("Update Book"):

            update_book(book_id, title, author, genre)

            st.success("Book Updated Successfully")

    # ==========================================================
    # DELETE BOOK
    # ==========================================================

    elif choice == "Delete Book":

        st.subheader("🗑 Delete Book")

        book_id = st.number_input(
            "Book ID",
            min_value=1,
            step=1
        )

        if st.button("Delete Book"):

            delete_book(book_id)

            st.success("Book Deleted Successfully")

    # ==========================================================
    # ISSUE BOOK
    # ==========================================================

    elif choice == "Issue Book":

        st.subheader("📤 Issue Book")

        # Get students
        students = get_students()

        student_dict = {f"{s[1]} (ID:{s[0]})": s[0] for s in students}

        selected_student = st.selectbox(
            "Select Student",
            list(student_dict.keys())
        )

        user_id = student_dict[selected_student]

        # Get books
        books = get_available_books()

        book_dict = {f"{b[1]} (ID:{b[0]})": b[0] for b in books}

        selected_book = st.selectbox(
            "Select Book",
            list(book_dict.keys())
        )

        book_id = book_dict[selected_book]

        if st.button("Issue Book"):
            result = issue_book(user_id, book_id)

            if result == "success":
                st.success("Book issued successfully!")
            else:
                st.error(result)
    # ==========================================================
    # RETURN BOOK
    # ==========================================================

    elif choice == "Return Book":

        st.subheader("📥 Return Book")

        students = get_students()

        if not students:
            st.warning("No students found.")

        else:

            student = st.selectbox(
                "Select Student",
                students,
                format_func=lambda x: x[1]
            )

            issued_books = get_issued_books(student[0])

            if not issued_books:

                st.info("This student has no issued books.")

            else:

                book = st.selectbox(
                    "Select Book",
                    issued_books,
                    format_func=lambda x: x[2]
                )

                if st.button("Return Book"):

                    return_book(book[0], book[1])

                    st.success("Book returned successfully!")

                    

    # ==========================================================
    # REPORTS
    # ==========================================================

    elif choice == "Reports":

        st.subheader("📄 Reports")

        st.write("Generate library reports.")

        if st.button("📥 Export Books to Excel"):

            file = export_books_excel()

            with open(file, "rb") as f:

                st.download_button(
                    label="Download Excel File",
                    data=f,
                    file_name=file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    # ==========================================================
    # LOGOUT
    # ==========================================================

    elif choice == "Logout":

        st.session_state["user"] = None
        st.session_state["role"] = None

        st.success("Logged Out Successfully")


    # ==========================================================
    # REPORTS
    # ==========================================================

    