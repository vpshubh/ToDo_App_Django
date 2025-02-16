import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect("todo.db")
cursor = conn.cursor()

# Create the tasks table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    completed INTEGER DEFAULT 0
)
""")
conn.commit()

# Add new columns if they don't exist
cursor.execute("PRAGMA table_info(tasks)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

if "due_date" not in column_names:
    cursor.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
if "priority" not in column_names:
    cursor.execute("ALTER TABLE tasks ADD COLUMN priority TEXT")
if "category" not in column_names:
    cursor.execute("ALTER TABLE tasks ADD COLUMN category TEXT")
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

# Entry widget for priority
priority_entry = tk.Entry(root, width=40, font=("Arial", 12))
priority_entry.pack(pady=5)

# Entry widget for category
category_entry = tk.Entry(root, width=40, font=("Arial", 12))
category_entry.pack(pady=5)

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

# Function to add a task
def add_task():
    task = task_entry.get()
    due_date = due_date_entry.get()
    priority = priority_entry.get()
    category = category_entry.get()

    if task:
        cursor.execute("""
            INSERT INTO tasks (task, due_date, priority, category)
            VALUES (?, ?, ?, ?)
        """, (task, due_date, priority, category))
        conn.commit()
        task_entry.delete(0, tk.END)
        due_date_entry.delete(0, tk.END)
        priority_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)
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

# Load tasks when the app starts
refresh_tasks()

# Save tasks when the app closes
root.protocol("WM_DELETE_WINDOW", lambda: [conn.close(), root.destroy()])

# Run the application
root.mainloop()