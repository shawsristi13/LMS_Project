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
    get_overdue_books,
    get_available_books
)

from report import export_books_excel


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

if "page" not in st.session_state:
    st.session_state["page"] = "Home"





# ==========================================================
# LOGIN PAGE
# ==========================================================
if st.session_state["user"] is None:
    st.header("📚 LibraryPRO")
    st.subheader("🔐 Login  to continue")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Select your role","admin", "student"])

    if st.button("Login"):
        user = login_user(email, password, role)

        if user:
            st.session_state["user"] = user
            st.session_state["role"] = role
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials (Make sure you have selected your role)")


# ==========================================================
# AFTER LOGIN
# ==========================================================
else:

    st.sidebar.success(
        f"Logged in as {st.session_state['role'].capitalize()}"
    )

    # ---------------- MENU ----------------

    if st.session_state["role"] == "admin":

        menu = [
            "Home",
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
            "Home",
            "Dashboard",
            "View Books",
            "Search Books",
            "My Borrowed Books",
            "Logout"
        ]

    # Sidebar Menu
    sidebar_choice = st.sidebar.selectbox(
        "📂 Navigation",
        menu,
        index=menu.index(st.session_state["page"]) if st.session_state["page"] in menu else 0
    )

    st.session_state["page"] = sidebar_choice
    choice = st.session_state["page"]

    st.success(
        f"Welcome back! Logged in as **{st.session_state['role'].capitalize()}**"
    )

    # ==========================================================
    # HOME PAGE
    # ==========================================================

    if choice == "Home":

        st.markdown("""
        <div class="main-card">

        <h1>📚 LibraryPRO</h1>

        <h3>Smart Library Management System</h3>

        <p>
        Manage Books • Users • Borrowing • Reports
        </p>

        </div>
        """, unsafe_allow_html=True)

        st.write("")

        
        st.markdown("## 🚀 Quick Access")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state["page"] = "Dashboard"
                st.rerun()

        with col2:
            if st.button("📚 View Books", use_container_width=True):
                st.session_state["page"] = "View Books"
                st.rerun()

        with col3:
            if st.session_state["role"] == "admin":
                if st.button("➕ Add Book", use_container_width=True):
                    st.session_state["page"] = "Add Book"
                    st.rerun()

        st.write("")

        if st.session_state["role"] == "admin":

            col4, col5, col6 = st.columns(3)

            with col4:
                if st.button("👥 User Management", use_container_width=True):
                    st.session_state["page"] = "User Management"
                    st.rerun()

            with col5:
                if st.button("📤 Issue Book", use_container_width=True):
                    st.session_state["page"] = "Issue Book"
                    st.rerun()

            with col6:
                if st.button("📥 Return Book", use_container_width=True):
                    st.session_state["page"] = "Return Book"
                    st.rerun()

            st.write("")

            col7, col8, col9 = st.columns(3)

            with col7:
                if st.button("🔍 Search Books", use_container_width=True):
                    st.session_state["page"] = "Search Books"
                    st.rerun()

            with col8:
                if st.button("📄 Reports", use_container_width=True):
                    st.session_state["page"] = "Reports"
                    st.rerun()

            with col9:
                if st.button("🚪 Logout", use_container_width=True):
                    st.session_state["user"] = None
                    st.session_state["role"] = None
                    st.session_state["page"] = "Home"
                    st.rerun()

        else:

            col4, col5, col6 = st.columns(3)

            with col4:
                if st.button("🔍 Search Books", use_container_width=True):
                    st.session_state["page"] = "Search Books"
                    st.rerun()

            with col5:
                if st.button("📖 My Borrowed Books", use_container_width=True):
                    st.session_state["page"] = "My Borrowed Books"
                    st.rerun()

            with col6:
                if st.button("🚪 Logout", use_container_width=True):
                    st.session_state["user"] = None
                    st.session_state["role"] = None
                    st.session_state["page"] = "Home"
                    st.rerun()

    # ==========================================================
    # DASHBOARD
    # ==========================================================
    elif choice == "Dashboard":

        st.subheader("📊 Dashboard")

        conn = get_connection()
        cur = conn.cursor()

        # Statistics
        cur.execute("SELECT COUNT(*) FROM books")
        total_books = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM books WHERE available = TRUE")
        available_books = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM transactions WHERE status='issued'")
        issued_books = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM users")
        total_users = cur.fetchone()[0]

        conn.close()

        # Metric Cards
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("📚 Total Books", total_books)
        col2.metric("✅ Available", available_books)
        col3.metric("📖 Issued", issued_books)
        col4.metric("👥 Users", total_users)

        st.divider()

        # Bar Chart
        chart_data = pd.DataFrame({
            "Category": ["Available", "Issued"],
            "Count": [available_books, issued_books]
        })

        fig = px.bar(
            chart_data,
            x="Category",
            y="Count",
            text="Count",
            title="Library Book Status"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Pie Chart
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT genre, COUNT(*)
            FROM books
            GROUP BY genre
        """)

        genre_data = cur.fetchall()
        conn.close()

        if genre_data:

            genre_df = pd.DataFrame(
                genre_data,
                columns=["Genre", "Books"]
            )

            fig2 = px.pie(
                genre_df,
                names="Genre",
                values="Books",
                title="Books by Genre"
            )

            st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        # Recently Added Books
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

            recent_df = pd.DataFrame(
                recent_books,
                columns=[
                    "Title",
                    "Author",
                    "Genre"
                ]
            )

            st.dataframe(
                recent_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No books available.")


        st.divider()

        st.subheader("⏰ Overdue Books")

        overdue = get_overdue_books()

        if overdue:

            df = pd.DataFrame(
                overdue,
                columns=[
                    "Student",
                    "Book",
                    "Issue Date",
                    "Due Date",
                    "Days Overdue"
                ]
            )

            st.dataframe(
                df,
                width="stretch",
                hide_index=True
            )

        else:

            st.success("🎉 No overdue books.")
    # ==========================================================
    # USER MANAGEMENT
    # ==========================================================
    elif choice == "User Management":

        st.subheader("👥 User Management Panel")

        tab1, tab2 = st.tabs(["➕ Add User", "📋 View Users"])

        # ======================================================
        # ADD USER TAB
        # ======================================================
        with tab1:

            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            role = st.selectbox("Role", ["student", "admin"])

            if st.button("Create User"):

                result = add_user(name, email, password, role)

                if result == "exists":
                    st.error("⚠️ Email already exists!")
                else:
                    st.success("✅ User created successfully!")

        # ======================================================
        # VIEW USERS TAB
        # ======================================================
        with tab2:

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT user_id, name, email, role
                FROM users
                ORDER BY user_id DESC
            """)

            users = cur.fetchall()
            conn.close()

            if users:

                df = pd.DataFrame(
                    users,
                    columns=["ID", "Name", "Email", "Role"]
                )

                st.dataframe(df, use_container_width=True)

                # ---------------- DELETE USER ----------------
                user_ids = [u[0] for u in users]
                selected_id = st.selectbox("Delete User ID", user_ids)

                if st.button("Delete User"):

                    conn = get_connection()
                    cur = conn.cursor()

                    cur.execute("DELETE FROM users WHERE user_id=%s", (selected_id,))

                    conn.commit()
                    conn.close()

                    st.success("User deleted successfully!")
                    st.rerun()

            else:
                st.info("No users found.")


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

        st.subheader("🔍 Search Books")

        keyword = st.text_input("Search by Title, Author or Genre")

        if keyword:

            books = search_books(keyword)

            if books:

                df = pd.DataFrame(
                    books,
                    columns=[
                        "Book ID",
                        "Title",
                        "Author",
                        "Genre",
                        "ISBN",
                        "Publisher",
                        "Year",
                        "Total Copies",
                        "Available",
                        "Shelf"
                    ]
                )

                st.dataframe(df, use_container_width=True)

            else:
                st.warning("No matching books found.")
    # ==========================================================
    # EDIT BOOKS
    # ==========================================================

    elif choice == "Edit Book":

        st.subheader("✏️ Edit Book")

        book_id = st.number_input("Book ID", min_value=1)

        title = st.text_input("New Title")
        author = st.text_input("New Author")
        genre = st.text_input("New Genre")

        if st.button("Update Book"):

            if title and author and genre:
                update_book(book_id, title, author, genre)
                st.success("Book updated successfully!")
            else:
                st.warning("Fill all fields")

    # ==========================================================
    # DELETE BOOKS
    # ==========================================================

    elif choice == "Delete Book":

        st.subheader("🗑 Delete Book")

        book_id = st.number_input("Book ID", min_value=1)

        if st.button("Delete Book"):

            delete_book(book_id)
            st.success("Book deleted successfully!")
    # ==========================================================
    # MY BORROWED BOOKS
    # ==========================================================
    elif choice == "My Borrowed Books":

        st.subheader("📖 My Borrowed Books")

        user_id = st.session_state["user"][0]

        books = get_borrowed_books(user_id)

        if books:

            df = pd.DataFrame(
                books,
                columns=[
                    "Title",
                    "Author",
                    "Issue Date",
                    "Due Date",
                    "Return Date",
                    "Status",
                    "Fine"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("📭 You have not borrowed any books yet.")


    # ==========================================================
    # ISSUE BOOK
    # ==========================================================
    elif choice == "Issue Book":

        st.subheader("📤 Issue Book")

        students = get_students()

        if not students:
            st.warning("No students found")
        else:

            student_dict = {f"{s[1]} (ID:{s[0]})": s[0] for s in students}
            selected_student = st.selectbox("Select Student", list(student_dict.keys()))
            user_id = student_dict[selected_student]

            books = get_available_books()

            if not books:
                st.warning("No available books")
            else:

                book_dict = {f"{b[1]} (ID:{b[0]})": b[0] for b in books}
                selected_book = st.selectbox("Select Book", list(book_dict.keys()))
                book_id = book_dict[selected_book]

                if st.button("Issue Book"):
                    result = issue_book(user_id, book_id)

                    if result == "success":
                        st.success("Book issued successfully")
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

            student = st.selectbox("Select Student", students, format_func=lambda x: x[1])

            issued_books = get_issued_books(student[0])

            if issued_books:

                df = pd.DataFrame(
                    issued_books,
                    columns=["Transaction ID", "Book ID", "Title"]
                )

                st.dataframe(df, use_container_width=True)

                book = st.selectbox(
                    "Select Book",
                    issued_books,
                    format_func=lambda x: x[2]
                )

                if st.button("Return Book"):

                    fine = return_book(book[0], book[1])

                    if fine > 0:
                        st.error(f"⚠ Fine Applied: ₹{fine}")
                    else:
                        st.success("Book returned successfully! No fine 🎉")
                    st.rerun()

            else:
                st.info("No issued books.")


    # ==========================================================
    # REPORTS
    # ==========================================================
    elif choice == "Reports":

        st.subheader("📊 Reports")

        books = get_books()

        if books:

            df = pd.DataFrame(
                books,
                columns=[
                    "Book ID",
                    "Title",
                    "Author",
                    "Genre",
                    "ISBN",
                    "Publisher",
                    "Year",
                    "Total Copies",
                    "Available",
                    "Shelf"
                ]
            )

            st.dataframe(df, use_container_width=True)

            if st.button("📥 Export Excel"):

                file = export_books_excel()

                with open(file, "rb") as f:
                    st.download_button(
                        "Download Report",
                        f,
                        file_name=file,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        else:
            st.info("No data available")


    # ==========================================================
    # LOGOUT
    # ==========================================================
    elif choice == "Logout":

        st.session_state["user"] = None
        st.session_state["role"] = None
        st.rerun()