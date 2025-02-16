import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
from datetime import datetime, timedelta
import csv

# Connect to the database
conn = sqlite3.connect("todo.db")
cursor = conn.cursor()

# Create tasks table
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

# Initialize main window
root = tk.Tk()
root.title("To-Do App")
root.minsize(800, 600)  # Minimum window size
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# ================= Responsive Layout =================
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Listbox with scrollbar
listbox_frame = tk.Frame(main_frame)
listbox_frame.pack(fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(listbox_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

task_listbox = tk.Listbox(
    listbox_frame, 
    yscrollcommand=scrollbar.set,
    font=("Arial", 12),
    selectbackground="#a6a6a6"
)
task_listbox.pack(fill=tk.BOTH, expand=True)
scrollbar.config(command=task_listbox.yview)

# Input fields
input_frame = tk.Frame(main_frame)
input_frame.pack(fill=tk.X, pady=10)

tk.Label(input_frame, text="Task:", width=8).pack(side=tk.LEFT)
task_entry = tk.Entry(input_frame, font=("Arial", 12))
task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

tk.Label(input_frame, text="Due Date:", width=8).pack(side=tk.LEFT)
due_date_entry = tk.Entry(input_frame, font=("Arial", 12))
due_date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

# Priority and Category dropdowns
dropdown_frame = tk.Frame(main_frame)
dropdown_frame.pack(fill=tk.X, pady=5)

priority_options = ["Low", "Medium", "High"]
tk.Label(dropdown_frame, text="Priority:").pack(side=tk.LEFT)
priority_combobox = ttk.Combobox(dropdown_frame, values=priority_options, width=12)
priority_combobox.pack(side=tk.LEFT, padx=5)
priority_combobox.set("Medium")

category_options = ["Work", "Personal", "Shopping", "Other"]
tk.Label(dropdown_frame, text="Category:").pack(side=tk.LEFT)
category_combobox = ttk.Combobox(dropdown_frame, values=category_options, width=12)
category_combobox.pack(side=tk.LEFT, padx=5)
category_combobox.set("Work")

# Action buttons
button_frame = tk.Frame(main_frame)
button_frame.pack(fill=tk.X, pady=10)

btn_style = {"width": 15, "height": 1}

add_btn = tk.Button(button_frame, text="➕ Add Task", **btn_style)
add_btn.pack(side=tk.LEFT, padx=5)

complete_btn = tk.Button(button_frame, text="✓ Complete", **btn_style)
complete_btn.pack(side=tk.LEFT, padx=5)

delete_btn = tk.Button(button_frame, text="🗑 Delete", **btn_style)
delete_btn.pack(side=tk.LEFT, padx=5)

# Filter/Sort buttons
action_frame = tk.Frame(main_frame)
action_frame.pack(fill=tk.X, pady=5)

filter_priority_btn = tk.Button(action_frame, text="Filter by Priority", width=15)
filter_priority_btn.pack(side=tk.LEFT, padx=2)

filter_category_btn = tk.Button(action_frame, text="Filter by Category", width=15)
filter_category_btn.pack(side=tk.LEFT, padx=2)

sort_due_date_btn = tk.Button(action_frame, text="Sort by Due Date", width=15)
sort_due_date_btn.pack(side=tk.LEFT, padx=2)

sort_priority_btn = tk.Button(action_frame, text="Sort by Priority", width=15)
sort_priority_btn.pack(side=tk.LEFT, padx=2)

# Bottom buttons
bottom_frame = tk.Frame(main_frame)
bottom_frame.pack(fill=tk.X, pady=10)

export_btn = tk.Button(bottom_frame, text="Export CSV", width=12)
export_btn.pack(side=tk.LEFT, padx=5)

check_due_dates_btn = tk.Button(bottom_frame, text="Check Due Dates", width=14)
check_due_dates_btn.pack(side=tk.LEFT, padx=5)

clear_all_btn = tk.Button(bottom_frame, text="Clear All", width=12)
clear_all_btn.pack(side=tk.LEFT, padx=5)

# ================= Core Functionality =================
def validate_due_date(due_date):
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def add_task():
    task = task_entry.get()
    due_date = due_date_entry.get()
    priority = priority_combobox.get()
    category = category_combobox.get()

    if task:
        if due_date and not validate_due_date(due_date):
            messagebox.showwarning("Warning", "Invalid date format. Use YYYY-MM-DD")
            return
            
        cursor.execute("""
            INSERT INTO tasks (task, due_date, priority, category)
            VALUES (?, ?, ?, ?)
        """, (task, due_date, priority, category))
        conn.commit()
        task_entry.delete(0, tk.END)
        due_date_entry.delete(0, tk.END)
        refresh_tasks()
    else:
        messagebox.showwarning("Warning", "Please enter a task")

def refresh_tasks():
    task_listbox.delete(0, tk.END)
    cursor.execute("SELECT id, task, due_date, priority, category, completed FROM tasks")
    tasks = cursor.fetchall()
    for task in tasks:
        task_id, task_text, due_date, priority, category, completed = task
        status = " ✔" if completed else ""
        task_listbox.insert(tk.END, 
            f"[{task_id}] {task_text} | Due: {due_date} | {priority} priority | {category}{status}")

def complete_task():
    try:
        selected = task_listbox.get(task_listbox.curselection())
        task_id = selected.split("]")[0][1:]
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        conn.commit()
        refresh_tasks()
    except:
        messagebox.showwarning("Warning", "Please select a task")

def delete_task():
    try:
        selected = task_listbox.get(task_listbox.curselection())
        task_id = selected.split("]")[0][1:]
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        refresh_tasks()
    except:
        messagebox.showwarning("Warning", "Please select a task")

def filter_tasks(criteria):
    filter_value = simpledialog.askstring("Filter", f"Enter {criteria}:")
    if filter_value:
        task_listbox.delete(0, tk.END)
        cursor.execute(f"SELECT * FROM tasks WHERE {criteria}=?", (filter_value,))
        tasks = cursor.fetchall()
        for task in tasks:
            task_id, task_text, due_date, priority, category, completed = task
            status = " ✔" if completed else ""
            task_listbox.insert(tk.END, 
                f"[{task_id}] {task_text} | Due: {due_date} | {priority} priority | {category}{status}")

def sort_tasks(criteria):
    task_listbox.delete(0, tk.END)
    cursor.execute(f"SELECT * FROM tasks ORDER BY {criteria}")
    tasks = cursor.fetchall()
    for task in tasks:
        task_id, task_text, due_date, priority, category, completed = task
        status = " ✔" if completed else ""
        task_listbox.insert(tk.END, 
            f"[{task_id}] {task_text} | Due: {due_date} | {priority} priority | {category}{status}")

def check_due_dates():
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT task, due_date FROM tasks WHERE due_date >= ? ORDER BY due_date", (today,))
    tasks = cursor.fetchall()
    if tasks:
        message = "Upcoming tasks:\n"
        for task, due_date in tasks:
            message += f"- {task} (Due: {due_date})\n"
        messagebox.showinfo("Upcoming Tasks", message)
    else:
        messagebox.showinfo("Upcoming Tasks", "No upcoming tasks found")

def export_tasks():
    with open('tasks.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Task', 'Due Date', 'Priority', 'Category', 'Completed'])
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        for task in tasks:
            writer.writerow(task)
    messagebox.showinfo("Export Successful", "Tasks exported to tasks.csv")

def clear_all_tasks():
    if messagebox.askyesno("Confirm", "Delete all tasks?"):
        cursor.execute("DELETE FROM tasks")
        conn.commit()
        refresh_tasks()

# Connect all buttons
add_btn.config(command=add_task)
complete_btn.config(command=complete_task)
delete_btn.config(command=delete_task)
filter_priority_btn.config(command=lambda: filter_tasks("priority"))
filter_category_btn.config(command=lambda: filter_tasks("category"))
sort_due_date_btn.config(command=lambda: sort_tasks("due_date"))
sort_priority_btn.config(command=lambda: sort_tasks("priority"))
export_btn.config(command=export_tasks)
check_due_dates_btn.config(command=check_due_dates)
clear_all_btn.config(command=clear_all_tasks)

# Initial load
refresh_tasks()

# Close handler
def on_close():
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()