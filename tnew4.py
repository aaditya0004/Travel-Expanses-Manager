import streamlit as st
import sqlite3
import random
import pandas as pd  # Import pandas for table formatting

# Set up page configuration
st.set_page_config(page_title="Travel Expense Manager", page_icon="✈️", layout="wide")

# Database connection
conn = sqlite3.connect('travel_expenses.db', check_same_thread=False)
c = conn.cursor()

# Create tables if not exist
c.execute('''CREATE TABLE IF NOT EXISTS trips (
                trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_name TEXT UNIQUE NOT NULL)''')
c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                FOREIGN KEY (trip_id) REFERENCES trips (trip_id) ON DELETE CASCADE)''')
conn.commit()

# Sidebar image
st.sidebar.image("sidebar.jpg", use_container_width=True)

# Title
st.title("✈️ Travel Expense Manager")
st.write("Easily track and manage your travel expenses!")
st.image("title1.png", use_container_width=True)

# Random travel quotes
travel_quotes = [
    "The world is a book, and those who do not travel read only one page. – Saint Augustine",
    "Travel is the only thing you buy that makes you richer. – Anonymous",
    "To travel is to live. – Hans Christian Andersen",
    "Life is either a daring adventure or nothing at all. – Helen Keller",
    "Adventure is worthwhile. – Aesop",
    "Travel far, travel wide, travel boldly. – Anonymous",
    "The journey not the arrival matters. – T.S. Eliot",
    "Take only memories, leave only footprints. – Chief Seattle",
    "Travel makes one modest. You see what a tiny place you occupy in the world. – Gustave Flaubert",
    "Wherever you go becomes a part of you somehow. – Anita Desai"
]

# Display a random travel quote in the sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🌍 Travel Quote of the Moment")
random_quote = random.choice(travel_quotes)
st.sidebar.markdown(f"*{random_quote}*")

# Menu options
menu_option = st.sidebar.selectbox("Select an Option", [
    "Add a New Trip", "Add Expenses", "View All Trips", "View Expenses", "Calculate Total Expenses", "Delete an Expense", "Delete a Trip"])

# Initialize a variable to display success messages at the top of the page
success_message = ""

# Functionality for each menu option
if menu_option == "Add a New Trip":
    trip_name = st.text_input("Enter trip name: ")
    if st.button("Add Trip"):
        try:
            c.execute("INSERT INTO trips (trip_name) VALUES (?)", (trip_name.upper(),))
            conn.commit()
            success_message = f"Trip '{trip_name.upper()}' added successfully!"
        except sqlite3.IntegrityError:
            success_message = f"Trip '{trip_name.upper()}' already exists."

elif menu_option == "Add Expenses":
    trips = [t[0] for t in c.execute("SELECT trip_name FROM trips").fetchall()]
    if trips:
        trip_name = st.selectbox("Select a Trip", trips)
        category = st.text_input("Enter expense category (Food, Transport, etc.)")
        amount = st.number_input("Enter amount", min_value=0.0, format="%.2f")
        description = st.text_area("Enter description")
        if st.button("Add Expense"):
            trip_id = c.execute("SELECT trip_id FROM trips WHERE trip_name = ?", (trip_name,)).fetchone()[0]
            c.execute("INSERT INTO expenses (trip_id, category, amount, description) VALUES (?, ?, ?, ?)",
                      (trip_id, category, amount, description))
            conn.commit()
            success_message = "Expense added successfully!"
    else:
        st.warning("No trips available. Please add a trip first.")

elif menu_option == "View All Trips":
    trips = c.execute("SELECT * FROM trips").fetchall()
    if trips:
        df = pd.DataFrame(trips, columns=["Trip ID", "Trip Name"])
        st.dataframe(df)
    else:
        st.warning("No trips found.")

elif menu_option == "View Expenses":
    trips = [t[0] for t in c.execute("SELECT trip_name FROM trips").fetchall()]
    if trips:
        trip_name = st.selectbox("Select a Trip", trips)
        trip_id = c.execute("SELECT trip_id FROM trips WHERE trip_name = ?", (trip_name,)).fetchone()[0]
        expenses = c.execute("SELECT id, category, amount, description FROM expenses WHERE trip_id = ?", (trip_id,)).fetchall()
        if expenses:
            df = pd.DataFrame(expenses, columns=["Expense ID", "Category", "Amount", "Description"])
            st.dataframe(df)
        else:
            st.warning("No expenses found for this trip.")
    else:
        st.warning("No trips available. Please add a trip first.")

elif menu_option == "Calculate Total Expenses":
    trips = [t[0] for t in c.execute("SELECT trip_name FROM trips").fetchall()]
    if trips:
        trip_name = st.selectbox("Select a Trip", trips)
        trip_id = c.execute("SELECT trip_id FROM trips WHERE trip_name = ?", (trip_name,)).fetchone()[0]
        totals = c.execute("SELECT category, SUM(amount) FROM expenses WHERE trip_id = ? GROUP BY category", (trip_id,)).fetchall()
        grand_total = c.execute("SELECT SUM(amount) FROM expenses WHERE trip_id = ?", (trip_id,)).fetchone()[0] or 0
        if totals:
            df_totals = pd.DataFrame(totals, columns=["Category", "Total Amount"])
            st.dataframe(df_totals)
            st.write(f"**Grand Total:** {grand_total}")
        else:
            st.warning("No expenses recorded for this trip.")
    else:
        st.warning("No trips available. Please add a trip first.")

elif menu_option == "Delete an Expense":
    trips = [t[0] for t in c.execute("SELECT trip_name FROM trips").fetchall()]
    if trips:
        trip_name = st.selectbox("Select a Trip", trips)
        trip_id = c.execute("SELECT trip_id FROM trips WHERE trip_name = ?", (trip_name,)).fetchone()[0]
        
        # Fetch expenses for the selected trip
        expenses = c.execute("SELECT id, category, amount, description FROM expenses WHERE trip_id = ?", (trip_id,)).fetchall()
        
        if expenses:
            expense_options = [f"ID: {expense[0]} | {expense[1]} | {expense[2]} | {expense[3]}" for expense in expenses]
            expense_to_delete = st.selectbox("Select an Expense to Delete", expense_options)
            
            # Extract the selected expense ID from the selected option
            selected_expense_id = int(expense_to_delete.split(" | ")[0].replace("ID:", "").strip())
            
            if st.button("Delete Expense"):
                c.execute("DELETE FROM expenses WHERE id = ?", (selected_expense_id,))
                conn.commit()
                success_message = f"Expense ID {selected_expense_id} deleted from trip '{trip_name}'."
        else:
            st.warning("No expenses found for this trip.")
    else:
        st.warning("No trips available. Please add a trip first.")


elif menu_option == "Delete a Trip":
    trips = [t[0] for t in c.execute("SELECT trip_name FROM trips").fetchall()]
    if trips:
        trip_name = st.selectbox("Select a Trip", trips)
        if st.button("Delete Trip"):
            trip_id = c.execute("SELECT trip_id FROM trips WHERE trip_name = ?", (trip_name,)).fetchone()[0]
            c.execute("DELETE FROM trips WHERE trip_id = ?", (trip_id,))
            conn.commit()
            success_message = f"Trip '{trip_name}' and all its expenses deleted successfully!"
    else:
        st.warning("No trips available.")

# Display success message at the top
if success_message:
    st.success(success_message)
