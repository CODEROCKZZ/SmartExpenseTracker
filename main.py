import tkinter as tk
import sqlite3
from tkinter import ttk
import matplotlib.pyplot as plt
import csv
from tkinter import filedialog

# ---------------- DATABASE ----------------

connection = sqlite3.connect("expenses.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS budget (
    id INTEGER PRIMARY KEY,
    amount REAL NOT NULL
)
""")

connection.commit()

monthly_budget = 0

cursor.execute(
    "SELECT amount FROM budget WHERE id = 1"
)

result = cursor.fetchone()

if result:
    monthly_budget = result[0]


# ---------------- WINDOW ----------------

window = tk.Tk()

window.title("Smart Personal Expense & Budget Tracker")
window.geometry("750x700")


# ---------------- FUNCTIONS ----------------

def add_expense():

    amount = amount_entry.get().strip()
    category = category_entry.get().strip()
    description = description_entry.get().strip()
    date = date_entry.get().strip()

    # Check required fields
    if amount == "" or category == "" or date == "":
        message_label.config(
            text="Please fill all required fields."
        )
        return

    # Check amount
    try:
        amount = float(amount)
    except ValueError:
        message_label.config(
            text="Amount must be a number."
        )
        return

    # Check positive amount
    if amount <= 0:
        message_label.config(
            text="Amount must be greater than 0."
        )
        return

    # Save expense
    cursor.execute("""
    INSERT INTO expenses (amount, category, description, date)
    VALUES (?, ?, ?, ?)
    """, (amount, category, description, date))

    connection.commit()

    message_label.config(
        text="Expense added successfully!"
    )

    # Clear fields
    amount_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)

def view_expenses():

    view_window = tk.Toplevel(window)

    view_window.title("View Expenses")
    view_window.geometry("750x450")

    columns = ("ID", "Amount", "Category", "Description", "Date")

    table = ttk.Treeview(
        view_window,
        columns=columns,
        show="headings"
    )

    for column in columns:
        table.heading(column, text=column)

    table.column("ID", width=50)
    table.column("Amount", width=100)
    table.column("Category", width=120)
    table.column("Description", width=200)
    table.column("Date", width=120)

    table.pack(fill="both", expand=True, padx=10, pady=10)

    cursor.execute("SELECT * FROM expenses")

    expenses = cursor.fetchall()

    for expense in expenses:
        table.insert("", tk.END, values=expense)


    # ---------------- DELETE FUNCTION ----------------

    def delete_expense():

        selected = table.selection()

        if not selected:
            message_label.config(text="Please select an expense")
            return

        selected_item = table.item(selected[0])

        expense_id = selected_item["values"][0]

        cursor.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )

        connection.commit()

        table.delete(selected[0])

        message_label.config(text="Expense deleted successfully!")


    # ---------------- EDIT FUNCTION ----------------

    def edit_expense():

        selected = table.selection()

        if not selected:
            message_label.config(text="Please select an expense")
            return

        selected_item = table.item(selected[0])

        values = selected_item["values"]

        edit_window = tk.Toplevel(view_window)

        edit_window.title("Edit Expense")
        edit_window.geometry("400x400")


        # Amount

        tk.Label(edit_window, text="Amount:").pack(pady=5)

        edit_amount = tk.Entry(edit_window)
        edit_amount.pack()

        edit_amount.insert(0, values[1])


        # Category

        tk.Label(edit_window, text="Category:").pack(pady=5)

        edit_category = tk.Entry(edit_window)
        edit_category.pack()

        edit_category.insert(0, values[2])


        # Description

        tk.Label(edit_window, text="Description:").pack(pady=5)

        edit_description = tk.Entry(edit_window)
        edit_description.pack()

        edit_description.insert(0, values[3])


        # Date

        tk.Label(edit_window, text="Date:").pack(pady=5)

        edit_date = tk.Entry(edit_window)
        edit_date.pack()

        edit_date.insert(0, values[4])


        # Update function

        def update_expense():

            new_amount = edit_amount.get()
            new_category = edit_category.get()
            new_description = edit_description.get()
            new_date = edit_date.get()

            cursor.execute("""
            UPDATE expenses
            SET amount = ?,
                category = ?,
                description = ?,
                date = ?
            WHERE id = ?
            """, (
                new_amount,
                new_category,
                new_description,
                new_date,
                values[0]
            ))

            connection.commit()

            table.item(
                selected[0],
                values=(
                    values[0],
                    new_amount,
                    new_category,
                    new_description,
                    new_date
                )
            )

            edit_window.destroy()

            message_label.config(
                text="Expense updated successfully!"
            )


        update_button = tk.Button(
            edit_window,
            text="Update Expense",
            command=update_expense
        )

        update_button.pack(pady=20)


    # ---------------- BUTTONS ----------------

    edit_button = tk.Button(
        view_window,
        text="Edit Expense",
        command=edit_expense
    )

    edit_button.pack(side=tk.LEFT, padx=20, pady=10)


    delete_button = tk.Button(
        view_window,
        text="Delete Expense",
        command=delete_expense
    )

    delete_button.pack(side=tk.RIGHT, padx=20, pady=10)
def set_budget():

    budget_window = tk.Toplevel(window)

    budget_window.title("Set Monthly Budget")
    budget_window.geometry("350x250")

    tk.Label(
        budget_window,
        text="Enter Monthly Budget:",
        font=("Arial", 12)
    ).pack(pady=20)

    budget_entry = tk.Entry(budget_window)

    budget_entry.pack(pady=5)

    def save_budget():

        global monthly_budget

        budget = budget_entry.get()

        if budget == "":
            budget_message.config(
                text="Please enter a budget"
            )
            return

        try:
            monthly_budget = float(budget)

            cursor.execute(
                "DELETE FROM budget"
            )

            cursor.execute(
                "INSERT INTO budget (id, amount) VALUES (1, ?)",
                (monthly_budget,)
            )

            connection.commit()

            budget_message.config(
                text="Budget saved successfully!"
            )

            budget_window.after(
                1000,
                budget_window.destroy
            )

        except ValueError:

            budget_message.config(
                text="Please enter a valid number"
            )

    save_button = tk.Button(
        budget_window,
        text="Save Budget",
        command=save_budget
    )

    save_button.pack(pady=15)

    budget_message = tk.Label(
        budget_window,
        text=""
    )

    budget_message.pack()    

def show_budget_summary():

    if monthly_budget == 0:

        message_label.config(
            text="Please set your monthly budget first"
        )

        return

    # Get total spending
    cursor.execute(
        "SELECT SUM(amount) FROM expenses"
    )

    result = cursor.fetchone()

    total_spent = result[0]

    if total_spent is None:
        total_spent = 0

    # Calculate remaining budget
    remaining = monthly_budget - total_spent

    # ---------------- BUDGET WARNING ----------------

    if total_spent > monthly_budget:

        warning = (
            f"⚠️ Budget exceeded by "
            f"₹{total_spent - monthly_budget:.2f}"
        )

    elif total_spent >= monthly_budget * 0.8:

        warning = "⚠️ You have used 80% or more of your budget."

    else:

        warning = "✅ You are within your budget."

    # ---------------- SUMMARY WINDOW ----------------

    summary_window = tk.Toplevel(window)

    summary_window.title("Budget Summary")

    summary_window.geometry("450x350")

    tk.Label(
        summary_window,
        text="Budget Summary",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    tk.Label(
        summary_window,
        text=f"Monthly Budget: ₹{monthly_budget:.2f}",
        font=("Arial", 14)
    ).pack(pady=10)

    tk.Label(
        summary_window,
        text=f"Total Spent: ₹{total_spent:.2f}",
        font=("Arial", 14)
    ).pack(pady=10)

    tk.Label(
        summary_window,
        text=f"Remaining: ₹{remaining:.2f}",
        font=("Arial", 14)
    ).pack(pady=10)

    tk.Label(
        summary_window,
        text=warning,
        font=("Arial", 12, "bold")
    ).pack(pady=15)

def category_analysis():

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)

    results = cursor.fetchall()

    if not results:
        message_label.config(
            text="No expenses available for analysis"
        )
        return

    categories = []
    totals = []

    for category, total in results:
        categories.append(category)
        totals.append(total)

    plt.figure(figsize=(8, 5))

    plt.bar(categories, totals)

    plt.title("Expense Analysis by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount Spent (₹)")

    plt.xticks(rotation=30)

    plt.tight_layout()

    plt.show()

def search_expenses():

    search_window = tk.Toplevel(window)

    search_window.title("Search Expenses")
    search_window.geometry("750x500")

    # Search label
    tk.Label(
        search_window,
        text="Search:",
        font=("Arial", 12)
    ).pack(pady=10)

    # Search entry
    search_entry = tk.Entry(
        search_window,
        width=40
    )

    search_entry.pack(pady=5)

    # Table
    columns = (
        "ID",
        "Amount",
        "Category",
        "Description",
        "Date"
    )

    table = ttk.Treeview(
        search_window,
        columns=columns,
        show="headings"
    )

    for column in columns:
        table.heading(column, text=column)

    table.column("ID", width=50)
    table.column("Amount", width=100)
    table.column("Category", width=120)
    table.column("Description", width=200)
    table.column("Date", width=120)

    table.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    # Search function
    def perform_search():

        search_text = search_entry.get()

        # Clear old results
        for item in table.get_children():
            table.delete(item)

        cursor.execute("""
        SELECT * FROM expenses
        WHERE category LIKE ?
           OR description LIKE ?
           OR date LIKE ?
        """, (
            "%" + search_text + "%",
            "%" + search_text + "%",
            "%" + search_text + "%"
        ))

        results = cursor.fetchall()

        for expense in results:
            table.insert(
                "",
                tk.END,
                values=expense
            )

    # Search button
    search_button = tk.Button(
        search_window,
        text="Search",
        command=perform_search
    )

    search_button.pack(pady=10)

def export_expenses():

    cursor.execute("SELECT * FROM expenses")

    expenses = cursor.fetchall()

    if not expenses:
        message_label.config(
            text="No expenses available to export"
        )
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
    )

    if file_path == "":
        return

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        # Header
        writer.writerow([
            "ID",
            "Amount",
            "Category",
            "Description",
            "Date"
        ])

        # Data
        writer.writerows(expenses)

    message_label.config(
        text="Expenses exported successfully!"
    )
# ---------------- TITLE ----------------

title_label = tk.Label(
    window,
    text="SMART PERSONAL EXPENSE & BUDGET TRACKER",
    font=("Arial", 20, "bold")
)

title_label.pack(pady=15)

subtitle_label = tk.Label(
    window,
    text="Manage your expenses, budget and spending analysis",
    font=("Arial", 11)
)

subtitle_label.pack(pady=5)

# ---------------- EXPENSE INPUT SECTION ----------------

expense_section = tk.Label(
    window,
    text="Add New Expense",
    font=("Arial", 14, "bold")
)

expense_section.pack(pady=10)


input_frame = tk.Frame(window)
input_frame.pack(pady=5)


# Amount

tk.Label(
    input_frame,
    text="Amount:",
    width=15,
    anchor="e"
).grid(row=0, column=0, padx=10, pady=5)

amount_entry = tk.Entry(
    input_frame,
    width=35
)

amount_entry.grid(row=0, column=1, padx=10, pady=5)


# Category

tk.Label(
    input_frame,
    text="Category:",
    width=15,
    anchor="e"
).grid(row=1, column=0, padx=10, pady=5)

category_entry = tk.Entry(
    input_frame,
    width=35
)

category_entry.grid(row=1, column=1, padx=10, pady=5)


# Description

tk.Label(
    input_frame,
    text="Description:",
    width=15,
    anchor="e"
).grid(row=2, column=0, padx=10, pady=5)

description_entry = tk.Entry(
    input_frame,
    width=35
)

description_entry.grid(row=2, column=1, padx=10, pady=5)


# Date

tk.Label(
    input_frame,
    text="Date:",
    width=15,
    anchor="e"
).grid(row=3, column=0, padx=10, pady=5)

date_entry = tk.Entry(
    input_frame,
    width=35
)

date_entry.grid(row=3, column=1, padx=10, pady=5)


# ---------------- BUTTONS ----------------

# ---------------- ADD EXPENSE BUTTON ----------------

add_button = tk.Button(
    window,
    text="Add Expense",
    command=add_expense
)

add_button.pack(pady=10)


# ---------------- EXPENSE MANAGEMENT ----------------



management_section = tk.Label(
    window,
    text="Expense Management",
    font=("Arial", 14, "bold")
)

management_section.pack(pady=10)

management_frame = tk.Frame(window)
management_frame.pack(pady=5)

view_button = tk.Button(
    management_frame,
    text="View Expenses",
    command=view_expenses,
    width=18
)
view_button.pack(side=tk.LEFT, padx=5)

search_button = tk.Button(
    management_frame,
    text="Search Expenses",
    command=search_expenses,
    width=18
)
search_button.pack(side=tk.LEFT, padx=5)

export_button = tk.Button(
    management_frame,
    text="Export Expenses",
    command=export_expenses,
    width=18
)
export_button.pack(side=tk.LEFT, padx=5)


# ---------------- BUDGET & ANALYSIS ----------------



analysis_section = tk.Label(
    window,
    text="Budget & Analysis",
    font=("Arial", 14, "bold")
)

analysis_section.pack(pady=10)

analysis_frame = tk.Frame(window)
analysis_frame.pack(pady=5)

budget_button = tk.Button(
    analysis_frame,
    text="Set Monthly Budget",
    command=set_budget,
    width=18
)
budget_button.pack(side=tk.LEFT, padx=5)

summary_button = tk.Button(
    analysis_frame,
    text="Budget Summary",
    command=show_budget_summary,
    width=18
)
summary_button.pack(side=tk.LEFT, padx=5)

analysis_button = tk.Button(
    analysis_frame,
    text="Category Analysis",
    command=category_analysis,
    width=18
)
analysis_button.pack(side=tk.LEFT, padx=5)
# ---------------- MESSAGE ----------------

message_label = tk.Label(window, text="")

message_label.pack(pady=10)


# ---------------- RUN ----------------

window.mainloop()

connection.close()