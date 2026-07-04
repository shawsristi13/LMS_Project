import streamlit as st
import pandas as pd
import plotly.express as px

from db import get_connection
from auth import login_user
from user import add_user, get_students
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
    calculate_fine,
    get_available_books
)

from report import export_books_excel
from config import APP_NAME


# ==========================================================
# LOAD CSS
# ==========================================================
def load_css():
    try:
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass

load_css()


# ==========================================================
# SESSION STATE
# ==========================================================
if "user" not in st.session_state:
    st.session_state["user"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None


# ==========================================================
# TITLE
# ==========================================================
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
            st.rerun()
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
    else:
        menu = [
            "Dashboard",
            "View Books",
            "Search Books",
            "My Borrowed Books",
            "Logout"
        ]

    choice = st.sidebar.selectbox("Menu", menu)

    st.markdown("## 👇 Select an option from sidebar")

    st.success(
        f"Welcome back! Logged in as **{st.session_state['role'].capitalize()}**"
    )


    # ==========================================================
    # DASHBOARD
    # ==========================================================
    if choice == "Dashboard":

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM books")
        total_books = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM transactions WHERE status='issued'")
        issued_books = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]

        conn.close()

        col1, col2, col3 = st.columns(3)
        col1.metric("📚 Books", total_books)
        col2.metric("📤 Issued", issued_books)
        col3.metric("👤 Users", total_users)


    # ==========================================================
    # USER MANAGEMENT
    # ==========================================================
    elif choice == "User Management":

        st.subheader("👥 User Management")

        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["student", "admin"])

        if st.button("Create User"):
            add_user(name, email, password, role)
            st.success("User created")


    # ==========================================================
    # ADD BOOK
    # ==========================================================
    elif choice == "Add Book":

        st.subheader("➕ Add Book")

        title = st.text_input("Title")
        author = st.text_input("Author")
        genre = st.text_input("Genre")

        if st.button("Add"):
            add_book(title, author, genre)
            st.success("Book added")


    # ==========================================================
    # VIEW BOOKS
    # ==========================================================
    elif choice == "View Books":

        st.subheader("📚 Books")

        books = get_books()

        df = pd.DataFrame(
            books,
            columns=[
                "Book ID",
                "Title",
                "Author",
                "Genre",
                "ISBN",
                "Publisher",
                "Publication Year",
                "Total Copies",
                "Available",
                "Shelf No"
            ]
        )

        df["Available"] = df["Available"].map({True: "✅ Yes", False: "❌ No"})

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        

    # ==========================================================
    # SEARCH
    # ==========================================================
    elif choice == "Search Books":

        keyword = st.text_input("Search")

        if keyword:
            books = search_books(keyword)
            st.write(books)


    # ==========================================================
    # MY BORROWED BOOKS
    # ==========================================================
    elif choice == "My Borrowed Books":

        user_id = st.session_state["user"][0]
        books = get_borrowed_books(user_id)

        st.dataframe(books)


    # ==========================================================
    # ISSUE BOOK
    # ==========================================================
    elif choice == "Issue Book":

        students = get_students()
        books = get_available_books()

        student = st.selectbox("Student", students, format_func=lambda x: x[1])
        book = st.selectbox("Book", books, format_func=lambda x: x[1])

        if st.button("Issue"):
            issue_book(student[0], book[0])
            st.success("Issued")


    # ==========================================================
    # RETURN BOOK
    # ==========================================================
    elif choice == "Return Book":

        st.subheader("Return Book")
        st.info("Working section")


    # ==========================================================
    # REPORTS
    # ==========================================================
    elif choice == "Reports":

        if st.button("Export Excel"):
            file = export_books_excel()
            st.success("Exported")


    # ==========================================================
    # LOGOUT
    # ==========================================================
    elif choice == "Logout":

        st.session_state["user"] = None
        st.session_state["role"] = None
        st.rerun()