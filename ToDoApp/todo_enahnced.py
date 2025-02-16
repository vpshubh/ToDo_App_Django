import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
from datetime import datetime, timedelta
import csv

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect("todo.db")
cursor = conn.cursor()

# Create the tasks table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    due_date TEXT,
    priority TEXT,
    category TEXT,
    completed INTEGER DEFAULT 0
)
""")
conn.commit()

# Initialize the main window
root = tk.Tk()
root.title("To-Do App")

# Add a label
label = tk.Label(root, text="Your To-Do List", font=("Arial", 16))
label.pack(pady=10)

# Listbox to display tasks
task_listbox = tk.Listbox(root, width=80, height=10, font=("Arial", 12))
task_listbox.pack(pady=10)

# Entry widget for adding tasks
task_entry = tk.Entry(root, width=40, font=("Arial", 12))
task_entry.pack(pady=5)

# Entry widget for due date
due_date_entry = tk.Entry(root, width=40, font=("Arial", 12))
due_date_entry.pack(pady=5)

# Dropdown for priority
priority_options = ["Low", "Medium", "High"]
priority_combobox = ttk.Combobox(root, values=priority_options, width=37, font=("Arial", 12))
priority_combobox.pack(pady=5)
priority_combobox.set("Low")  # Default value

# Dropdown for category
category_options = ["Work", "Personal", "Shopping", "Other"]
category_combobox = ttk.Combobox(root, values=category_options, width=37, font=("Arial", 12))
category_combobox.pack(pady=5)
category_combobox.set("Work")  # Default value

# Function to validate due date format
def validate_due_date(due_date):
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# Function to add a task
def add_task():
    task = task_entry.get()
    due_date = due_date_entry.get()
    priority = priority_combobox.get()
    category = category_combobox.get()

    if task:
        if due_date and not validate_due_date(due_date):
            messagebox.showwarning("Warning", "Invalid due date format. Please use YYYY-MM-DD.")
            return
        cursor.execute("""
            INSERT INTO tasks (task, due_date, priority, category)
            VALUES (?, ?, ?, ?)
        """, (task, due_date, priority, category))
        conn.commit()
        task_entry.delete(0, tk.END)
        due_date_entry.delete(0, tk.END)
        priority_combobox.set("Low")  # Reset to default
        category_combobox.set("Work")  # Reset to default
        refresh_tasks()
    else:
        messagebox.showwarning("Warning", "Please enter a task.")

# Function to mark a task as completed
def complete_task():
    try:
        selected_task = task_listbox.get(task_listbox.curselection())
        task_id = selected_task.split(":")[0]
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        conn.commit()
        refresh_tasks()
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to mark as completed.")

# Function to delete a task
def delete_task():
    try:
        selected_task = task_listbox.get(task_listbox.curselection())
        task_id = selected_task.split(":")[0]
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        refresh_tasks()
    except IndexError:
        messagebox.showwarning("Warning", "Please select a task to delete.")

# Function to refresh the listbox with tasks from the database
def refresh_tasks():
    task_listbox.delete(0, tk.END)
    cursor.execute("SELECT id, task, due_date, priority, category, completed FROM tasks")
    tasks = cursor.fetchall()
    for task in tasks:
        task_id, task_text, due_date, priority, category, completed = task
        status = " (Completed)" if completed else ""
        task_listbox.insert(tk.END, f"{task_id}: {task_text} | Due: {due_date} | Priority: {priority} | Category: {category}{status}")

# Function to filter tasks
def filter_tasks(criteria):
    filter_value = simpledialog.askstring(f"Filter by {criteria.capitalize()}", f"Enter {criteria}:")
    if filter_value:
        task_listbox.delete(0, tk.END)
        cursor.execute(f"SELECT id, task, due_date, priority, category, completed FROM tasks WHERE {criteria} = ?", (filter_value,))
        tasks = cursor.fetchall()
        for task in tasks:
            task_id, task_text, due_date, priority, category, completed = task
            status = " (Completed)" if completed else ""
            task_listbox.insert(tk.END, f"{task_id}: {task_text} | Due: {due_date} | Priority: {priority} | Category: {category}{status}")

# Function to sort tasks
def sort_tasks(criteria):
    task_listbox.delete(0, tk.END)
    cursor.execute(f"SELECT id, task, due_date, priority, category, completed FROM tasks ORDER BY {criteria}")
    tasks = cursor.fetchall()
    for task in tasks:
        task_id, task_text, due_date, priority, category, completed = task
        status = " (Completed)" if completed else ""
        task_listbox.insert(tk.END, f"{task_id}: {task_text} | Due: {due_date} | Priority: {priority} | Category: {category}{status}")

# Function to check for upcoming due dates
def check_due_dates():
    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    cursor.execute("SELECT task, due_date FROM tasks WHERE due_date BETWEEN ? AND ?", (now.strftime("%Y-%m-%d"), tomorrow.strftime("%Y-%m-%d")))
    upcoming_tasks = cursor.fetchall()
    if upcoming_tasks:
        message = "Upcoming tasks:\n"
        for task, due_date in upcoming_tasks:
            message += f"- {task} (Due: {due_date})\n"
        messagebox.showinfo("Upcoming Due Dates", message)
    else:
        messagebox.showinfo("Upcoming Due Dates", "No tasks due in the next 24 hours.")

# Function to export tasks to a CSV file
def export_tasks():
    with open("tasks.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Task", "Due Date", "Priority", "Category", "Completed"])
        cursor.execute("SELECT id, task, due_date, priority, category, completed FROM tasks")
        tasks = cursor.fetchall()
        for task in tasks:
            writer.writerow(task)
    messagebox.showinfo("Export Successful", "Tasks have been exported to tasks.csv.")

# Function to clear all tasks
def clear_all_tasks():
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete all tasks?")
    if confirm:
        cursor.execute("DELETE FROM tasks")
        conn.commit()
        refresh_tasks()

# Function to search tasks
def search_tasks(keyword):
    task_listbox.delete(0, tk.END)
    cursor.execute("SELECT id, task, due_date, priority, category, completed FROM tasks WHERE task LIKE ?", (f"%{keyword}%",))
    tasks = cursor.fetchall()
    for task in tasks:
        task_id, task_text, due_date, priority, category, completed = task
        status = " (Completed)" if completed else ""
        task_listbox.insert(tk.END, f"{task_id}: {task_text} | Due: {due_date} | Priority: {priority} | Category: {category}{status}")

# Button to add a task
add_button = tk.Button(root, text="Add Task", width=20, command=lambda: add_task())
add_button.pack(pady=5)

# Button to mark a task as completed
complete_button = tk.Button(root, text="Mark as Completed", width=20, command=lambda: complete_task())
complete_button.pack(pady=5)

# Button to delete a task
delete_button = tk.Button(root, text="Delete Task", width=20, command=lambda: delete_task())
delete_button.pack(pady=5)

# Button to filter by priority
filter_priority_button = tk.Button(root, text="Filter by Priority", width=20, command=lambda: filter_tasks("priority"))
filter_priority_button.pack(pady=5)

# Button to filter by category
filter_category_button = tk.Button(root, text="Filter by Category", width=20, command=lambda: filter_tasks("category"))
filter_category_button.pack(pady=5)

# Button to sort by due date
sort_due_date_button = tk.Button(root, text="Sort by Due Date", width=20, command=lambda: sort_tasks("due_date"))
sort_due_date_button.pack(pady=5)

# Button to sort by priority
sort_priority_button = tk.Button(root, text="Sort by Priority", width=20, command=lambda: sort_tasks("priority"))
sort_priority_button.pack(pady=5)

# Button to check due dates
due_date_notification_button = tk.Button(root, text="Check Due Dates", width=20, command=check_due_dates)
due_date_notification_button.pack(pady=5)

# Button to export tasks
export_button = tk.Button(root, text="Export Tasks", width=20, command=export_tasks)
export_button.pack(pady=5)

# Button to clear all tasks
clear_all_button = tk.Button(root, text="Clear All Tasks", width=20, command=clear_all_tasks)
clear_all_button.pack(pady=5)

# Entry widget for search
search_entry = tk.Entry(root, width=40, font=("Arial", 12))
search_entry.pack(pady=5)

# Button to search tasks
search_button = tk.Button(root, text="Search Tasks", width=20, command=lambda: search_tasks(search_entry.get()))
search_button.pack(pady=5)

# Load tasks when the app starts
refresh_tasks()

# Check for upcoming due dates when the app starts
check_due_dates()

# Save tasks when the app closes
root.protocol("WM_DELETE_WINDOW", lambda: [conn.close(), root.destroy()])

# Run the application
root.mainloop()