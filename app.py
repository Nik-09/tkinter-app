#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import mysql.connector

# ---------------- DB Connection ----------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="school_admin",   # MySQL username
        password="admin123",   # MySQL password
        database="fees"        # Your DB name
    )

# ---------------- Fetch Defaulters ----------------
def get_defaulters(selected_class, selected_month, min_due):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT s.name, s.phone, s.class, s.category, p.month,
           (f.standard_fee - p.amount_paid) AS due_amount
        FROM students s
        JOIN payments p ON s.id = p.student_id
        JOIN fees f ON s.class = f.class
            AND (s.category = f.category OR f.category IS NULL)
        WHERE (f.standard_fee - p.amount_paid) > %s
    """
    params = [min_due]

    if selected_class != "All":
        query += " AND s.class = %s"
        params.append(selected_class)

    if selected_month != "All":
        query += " AND p.month = %s"
        params.append(selected_month)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------------- Apply Filter ----------------
def apply_filter():
    for row in table.get_children():
        table.delete(row)
    rows = get_defaulters(class_var.get(), month_var.get(), int(due_var.get()))
    for r in rows:
        table.insert("", "end", values=r)

# ---------------- Tkinter Window ----------------
root = tk.Tk()
root.title("Fee Defaulter Manager")
root.configure(bg="#f0f4f8")  # Light background
root.geometry("1100x600")  # Enough width to show all columns

# ---------------- Style ----------------
style = ttk.Style()
style.theme_use("clam")

# Treeview Style
style.configure(
    "Treeview",
    background="#ffffff",
    foreground="#000000",
    rowheight=25,
    fieldbackground="#ffffff",
    font=("Segoe UI", 10)
)
style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 11, "bold"),
    background="#4a90e2",
    foreground="white"
)
style.map("Treeview", background=[("selected", "#4a90e2")])

# Button Style
style.configure(
    "TButton",
    font=("Segoe UI", 10, "bold"),
    padding=6,
    background="#4a90e2",
    foreground="white"
)
style.map(
    "TButton",
    background=[("active", "#357ABD")],
    foreground=[("active", "white")]
)

# Combobox Style
style.configure("TCombobox",
                fieldbackground="white",
                background="lightblue",
                foreground="black",
                arrowcolor="blue",
                padding=5)

# ---------------- Reset Filters ----------------
def reset_filters():
    # Clear table
    for row in table.get_children():
        table.delete(row)

    # Reset filter variables
    class_var.set("All")
    month_var.set("All")
    due_var.set("0")


# ---------------- Filters Frame ----------------
class_var = tk.StringVar(value="All")
month_var = tk.StringVar(value="All")
due_var = tk.StringVar(value="0")

filter_frame = tk.Frame(root, bg="#f0f4f8")
filter_frame.grid(row=0, column=0, columnspan=7, pady=10, sticky="w")

# Class filter
tk.Label(filter_frame, text="Class:", bg="#f0f4f8", font=("Segoe UI", 10)).grid(row=0, column=0, padx=5)
ttk.Combobox(filter_frame, textvariable=class_var,
             values=["All", "8", "9", "10", "11", "12"],
             state="readonly", style="TCombobox").grid(row=0, column=1, padx=5, pady=5)

# Month filter
tk.Label(filter_frame, text="Month:", bg="#f0f4f8", font=("Segoe UI", 10)).grid(row=0, column=2, padx=5)
ttk.Combobox(filter_frame, textvariable=month_var,
             values=["All", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
             state="readonly", style="TCombobox").grid(row=0, column=3, padx=5, pady=5)

# Due filter
tk.Label(filter_frame, text="Due >", bg="#f0f4f8", font=("Segoe UI", 10)).grid(row=0, column=4, padx=5)
tk.Entry(filter_frame, textvariable=due_var, width=7, font=("Segoe UI", 10)).grid(row=0, column=5, padx=5)

# Apply Filter button
ttk.Button(filter_frame, text="Apply Filter", style="TButton", command=apply_filter).grid(row=0, column=6, padx=5)
ttk.Button(filter_frame, text="Reset", style="TButton", command=reset_filters).grid(row=0, column=7, padx=5)

# ---------------- Table ----------------
columns = ("Name", "Phone", "Class", "Category", "Month Due", "Due Amount")
table_frame = tk.Frame(root, bg="#f0f4f8")
table_frame.grid(row=1, column=0, columnspan=7, sticky="nsew", padx=10, pady=10)

table = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
for col in columns:
    table.heading(col, text=col)
    table.column(col, width=150)
table.pack(fill="both", expand=True)

# Scrollbars
scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview)
table.configure(yscroll=scroll_y.set, xscroll=scroll_x.set)
scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")

# Run the app
root.mainloop()
