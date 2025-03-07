import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime, timedelta
import csv

# ================= Constants & Styles =================
COLOR_SCHEME = {
    "primary": "#2c3e50",
    "secondary": "#34495e",
    "accent": "#3498db",
    "success": "#27ae60",
    "warning": "#f1c40f",
    "danger": "#e74c3c",
    "light": "#ecf0f1",
    "dark": "#2c3e50",
    "text": "#ffffff"
}

FONT_SCHEME = {
    "title": ("Segoe UI", 16, "bold"),
    "body": ("Segoe UI", 12),
    "button": ("Segoe UI", 11, "bold"),
    "small": ("Segoe UI", 10)
}

PADDING = {
    "xsmall": 3,
    "small": 5,
    "medium": 10,
    "large": 15
}

TIME_OPTIONS = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 15, 30, 45)]

# ================= Database Setup =================
conn = sqlite3.connect("todo.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    due_date TEXT,
    due_time TEXT,
    priority TEXT,
    category TEXT,
    completed INTEGER DEFAULT 0,
    recurrence TEXT,
    notes TEXT
)
""")

# Check for missing columns
cursor.execute("PRAGMA table_info(tasks)")
columns = [column[1] for column in cursor.fetchall()]
if 'due_time' not in columns:
    cursor.execute("ALTER TABLE tasks ADD COLUMN due_time TEXT")
if 'category' not in columns:
    cursor.execute("ALTER TABLE tasks ADD COLUMN category TEXT")
if 'recurrence' not in columns:
    cursor.execute("ALTER TABLE tasks ADD COLUMN recurrence TEXT")
if 'notes' not in columns:
    cursor.execute("ALTER TABLE tasks ADD COLUMN notes TEXT")

conn.commit()

# ================= Main Application =================
class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced To-Do App")
        self.root.geometry("1200x800")
        self.sort_column = None
        self.sort_reverse = False
        
        # Create main frames
        self.input_frame = tk.Frame(root, bg=COLOR_SCHEME["primary"])
        self.view_frame = tk.Frame(root, bg=COLOR_SCHEME["primary"])
        
        self.setup_input_view()
        self.setup_full_view()
        self.show_input_view()
        self.refresh_tasks()

    def setup_input_view(self):
        input_container = tk.Frame(self.input_frame, bg=COLOR_SCHEME["primary"])
        input_container.pack(pady=50, padx=50, fill=tk.BOTH, expand=True)

        # Header
        header = tk.Label(input_container, text="Add New Task", 
                         bg=COLOR_SCHEME["secondary"], fg=COLOR_SCHEME["text"],
                         font=FONT_SCHEME["title"], padx=20, pady=10)
        header.pack(fill=tk.X)

        # Task Input
        task_frame = tk.Frame(input_container, bg=COLOR_SCHEME["primary"])
        task_frame.pack(pady=PADDING["medium"], fill=tk.X)
        tk.Label(task_frame, text="Task:", bg=COLOR_SCHEME["primary"], 
                fg=COLOR_SCHEME["text"], font=FONT_SCHEME["body"]).pack(side=tk.LEFT)
        self.task_entry = tk.Entry(task_frame, font=FONT_SCHEME["body"], 
                                  bg=COLOR_SCHEME["light"], width=40)
        self.task_entry.pack(side=tk.LEFT, padx=PADDING["medium"])

        # Date and Time
        datetime_frame = tk.Frame(input_container, bg=COLOR_SCHEME["primary"])
        datetime_frame.pack(pady=PADDING["medium"], fill=tk.X)
        
        # Date Picker
        tk.Label(datetime_frame, text="Due Date:", bg=COLOR_SCHEME["primary"], 
                fg=COLOR_SCHEME["text"], font=FONT_SCHEME["body"]).pack(side=tk.LEFT)
        self.due_date_cal = DateEntry(
            datetime_frame,
            date_pattern="yyyy-mm-dd",
            font=FONT_SCHEME["body"],
            background=COLOR_SCHEME["dark"],
            foreground=COLOR_SCHEME["text"],
            borderwidth=1,
            relief=tk.FLAT
        )
        self.due_date_cal.pack(side=tk.LEFT, padx=PADDING["medium"])

        # Time Picker
        tk.Label(datetime_frame, text="Time:", bg=COLOR_SCHEME["primary"], 
                fg=COLOR_SCHEME["text"], font=FONT_SCHEME["body"]).pack(side=tk.LEFT)
        self.due_time_combo = ttk.Combobox(
            datetime_frame,
            values=TIME_OPTIONS,
            font=FONT_SCHEME["body"],
            state="readonly",
            width=8
        )
        self.due_time_combo.set("00:00")
        self.due_time_combo.pack(side=tk.LEFT, padx=PADDING["medium"])

        # Priority & Category
        dropdown_frame = tk.Frame(input_container, bg=COLOR_SCHEME["primary"])
        dropdown_frame.pack(pady=PADDING["medium"], fill=tk.X)
        
        # Priority
        tk.Label(dropdown_frame, text="Priority:", bg=COLOR_SCHEME["primary"], 
                fg=COLOR_SCHEME["text"], font=FONT_SCHEME["body"]).pack(side=tk.LEFT)
        self.priority_combo = ttk.Combobox(
            dropdown_frame,
            values=["Low", "Medium", "High"],
            font=FONT_SCHEME["body"],
            state="readonly",
            width=10
        )
        self.priority_combo.set("Medium")
        self.priority_combo.pack(side=tk.LEFT, padx=PADDING["medium"])

        # Category
        tk.Label(dropdown_frame, text="Category:", bg=COLOR_SCHEME["primary"], 
                fg=COLOR_SCHEME["text"], font=FONT_SCHEME["body"]).pack(side=tk.LEFT)
        self.category_combo = ttk.Combobox(
            dropdown_frame,
            values=["Work", "Personal", "Shopping", "Other"],
            font=FONT_SCHEME["body"],
            state="readonly",
            width=10
        )
        self.category_combo.set("Work")
        self.category_combo.pack(side=tk.LEFT, padx=PADDING["medium"])

        # Recurrence
        tk.Label(dropdown_frame, text="Recurrence:", bg=COLOR_SCHEME["primary"], 
                fg=COLOR_SCHEME["text"], font=FONT_SCHEME["body"]).pack(side=tk.LEFT)
        self.recurrence_combo = ttk.Combobox(
            dropdown_frame,
            values=["None", "Daily", "Weekly", "Monthly"],
            font=FONT_SCHEME["body"],
            state="readonly",
            width=10
        )
        self.recurrence_combo.set("None")
        self.recurrence_combo.pack(side=tk.LEFT, padx=PADDING["medium"])

        # Notes
        notes_frame = tk.Frame(input_container, bg=COLOR_SCHEME["primary"])
        notes_frame.pack(pady=PADDING["medium"], fill=tk.X)
        tk.Label(notes_frame, text="Notes:", bg=COLOR_SCHEME["primary"], 
                fg=COLOR_SCHEME["text"], font=FONT_SCHEME["body"]).pack(side=tk.LEFT)
        self.notes_entry = tk.Text(notes_frame, font=FONT_SCHEME["body"], 
                                  bg=COLOR_SCHEME["light"], width=40, height=4)
        self.notes_entry.pack(side=tk.LEFT, padx=PADDING["medium"])

        # Buttons
        add_btn = tk.Button(input_container, text="➕ Add Task", command=self.add_task,
                           bg=COLOR_SCHEME["success"], fg=COLOR_SCHEME["text"],
                           font=FONT_SCHEME["button"], relief=tk.FLAT, padx=20)
        add_btn.pack(pady=PADDING["large"])

        view_btn = tk.Button(input_container, text="📋 View All Tasks", 
                            command=self.show_full_view,
                            bg=COLOR_SCHEME["accent"], fg=COLOR_SCHEME["text"],
                            font=FONT_SCHEME["button"], relief=tk.FLAT)
        view_btn.pack(pady=PADDING["medium"])

    def setup_full_view(self):
        view_container = tk.Frame(self.view_frame, bg=COLOR_SCHEME["primary"])
        view_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Back Button
        back_btn = tk.Button(view_container, text="← Back to Add Task", 
                            command=self.show_input_view,
                            bg=COLOR_SCHEME["secondary"], fg=COLOR_SCHEME["text"],
                            font=FONT_SCHEME["button"], relief=tk.FLAT)
        back_btn.pack(anchor="nw", pady=10)

        # Filter Frame
        filter_frame = tk.Frame(view_container, bg=COLOR_SCHEME["primary"])
        filter_frame.pack(fill=tk.X, pady=10)

        tk.Label(filter_frame, text="Filter by:", bg=COLOR_SCHEME["primary"], 
                fg=COLOR_SCHEME["text"], font=FONT_SCHEME["body"]).pack(side=tk.LEFT)

        self.filter_priority_combo = ttk.Combobox(
            filter_frame,
            values=["All", "Low", "Medium", "High"],
            font=FONT_SCHEME["body"],
            state="readonly",
            width=10
        )
        self.filter_priority_combo.set("All")
        self.filter_priority_combo.pack(side=tk.LEFT, padx=PADDING["medium"])

        self.filter_category_combo = ttk.Combobox(
            filter_frame,
            values=["All", "Work", "Personal", "Shopping", "Other"],
            font=FONT_SCHEME["body"],
            state="readonly",
            width=10
        )
        self.filter_category_combo.set("All")
        self.filter_category_combo.pack(side=tk.LEFT, padx=PADDING["medium"])

        self.filter_status_combo = ttk.Combobox(
            filter_frame,
            values=["All", "Pending", "Complete"],
            font=FONT_SCHEME["body"],
            state="readonly",
            width=10
        )
        self.filter_status_combo.set("All")
        self.filter_status_combo.pack(side=tk.LEFT, padx=PADDING["medium"])

        filter_btn = tk.Button(filter_frame, text="Apply Filters", 
                              command=self.refresh_tasks,
                              bg=COLOR_SCHEME["accent"], fg=COLOR_SCHEME["text"],
                              font=FONT_SCHEME["button"], relief=tk.FLAT)
        filter_btn.pack(side=tk.LEFT, padx=PADDING["medium"])

        # Search Frame
        search_frame = tk.Frame(view_container, bg=COLOR_SCHEME["primary"])
        search_frame.pack(fill=tk.X, pady=10)

        tk.Label(search_frame, text="Search:", bg=COLOR_SCHEME["primary"], 
                fg=COLOR_SCHEME["text"], font=FONT_SCHEME["body"]).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, font=FONT_SCHEME["body"], 
                                   bg=COLOR_SCHEME["light"], width=40)
        self.search_entry.pack(side=tk.LEFT, padx=PADDING["medium"])

        search_btn = tk.Button(search_frame, text="🔍 Search", 
                              command=self.refresh_tasks,
                              bg=COLOR_SCHEME["accent"], fg=COLOR_SCHEME["text"],
                              font=FONT_SCHEME["button"], relief=tk.FLAT)
        search_btn.pack(side=tk.LEFT, padx=PADDING["medium"])

        # Treeview Container
        tree_container = tk.Frame(view_container)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # Treeview Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background=COLOR_SCHEME["light"],
                        fieldbackground=COLOR_SCHEME["light"],
                        font=FONT_SCHEME["body"],
                        rowheight=30)
        style.configure("Treeview.Heading", 
                        background=COLOR_SCHEME["secondary"],
                        foreground=COLOR_SCHEME["text"],
                        font=FONT_SCHEME["button"])
        style.map("Treeview", background=[("selected", COLOR_SCHEME["accent"])])

        # Task Tree
        self.task_tree = ttk.Treeview(tree_container, 
                                    columns=("ID", "Task", "Due Date", "Time", "Priority", "Category", "Status", "Recurrence", "Notes"), 
                                    show="headings", selectmode="browse")
        
        # Configure columns
        columns = ("ID", "Task", "Due Date", "Time", "Priority", "Category", "Status", "Recurrence", "Notes")
        for col in columns:
            self.task_tree.heading(col, text=col, anchor="w", 
                                  command=lambda c=col: self.treeview_sort_column(c))
            self.task_tree.column(col, anchor="w")

        self.task_tree.column("ID", width=80)
        self.task_tree.column("Task", width=400)
        self.task_tree.column("Due Date", width=150)
        self.task_tree.column("Time", width=100)
        self.task_tree.column("Priority", width=120)
        self.task_tree.column("Category", width=150)
        self.task_tree.column("Status", width=120)
        self.task_tree.column("Recurrence", width=120)
        self.task_tree.column("Notes", width=300)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.task_tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Layout using grid
        self.task_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Action Buttons
        action_frame = tk.Frame(view_container, bg=COLOR_SCHEME["primary"])
        action_frame.pack(fill=tk.X, pady=10)

        complete_btn = tk.Button(action_frame, text="✅ Complete Task", 
                                command=self.complete_task,
                                bg=COLOR_SCHEME["success"], fg=COLOR_SCHEME["text"],
                                font=FONT_SCHEME["button"], relief=tk.FLAT)
        complete_btn.pack(side=tk.LEFT, padx=5)

        edit_btn = tk.Button(action_frame, text="✏️ Edit Task", 
                            command=self.edit_task,
                            bg=COLOR_SCHEME["warning"], fg=COLOR_SCHEME["text"],
                            font=FONT_SCHEME["button"], relief=tk.FLAT)
        edit_btn.pack(side=tk.LEFT, padx=5)

        delete_btn = tk.Button(action_frame, text="❌ Delete Task", 
                              command=self.delete_task,
                              bg=COLOR_SCHEME["danger"], fg=COLOR_SCHEME["text"],
                              font=FONT_SCHEME["button"], relief=tk.FLAT)
        delete_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(action_frame, text="🧹 Clear All Tasks", 
                              command=self.clear_all_tasks,
                              bg=COLOR_SCHEME["warning"], fg=COLOR_SCHEME["text"],
                              font=FONT_SCHEME["button"], relief=tk.FLAT)
        clear_btn.pack(side=tk.LEFT, padx=5)

        export_btn = tk.Button(action_frame, text="📤 Export Tasks", 
                              command=self.export_tasks,
                              bg=COLOR_SCHEME["accent"], fg=COLOR_SCHEME["text"],
                              font=FONT_SCHEME["button"], relief=tk.FLAT)
        export_btn.pack(side=tk.LEFT, padx=5)

        import_btn = tk.Button(action_frame, text="📥 Import Tasks", 
                              command=self.import_tasks,
                              bg=COLOR_SCHEME["accent"], fg=COLOR_SCHEME["text"],
                              font=FONT_SCHEME["button"], relief=tk.FLAT)
        import_btn.pack(side=tk.LEFT, padx=5)

    def show_input_view(self):
        self.view_frame.pack_forget()
        self.input_frame.pack(fill=tk.BOTH, expand=True)
        self.root.geometry("800x600")

    def show_full_view(self):
        self.input_frame.pack_forget()
        self.view_frame.pack(fill=tk.BOTH, expand=True)
        self.root.geometry("1200x800")
        self.refresh_tasks()

    def add_task(self):
        task = self.task_entry.get()
        due_date = self.due_date_cal.get_date().strftime("%Y-%m-%d")
        due_time = self.due_time_combo.get()
        priority = self.priority_combo.get()
        category = self.category_combo.get()
        recurrence = self.recurrence_combo.get()
        notes = self.notes_entry.get("1.0", tk.END).strip()

        if task:
            cursor.execute("""
                INSERT INTO tasks (task, due_date, due_time, priority, category, recurrence, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (task, due_date, due_time, priority, category, recurrence, notes))
            conn.commit()
            self.task_entry.delete(0, tk.END)
            self.notes_entry.delete("1.0", tk.END)
            messagebox.showinfo("Success", "Task added successfully!")
            self.refresh_tasks()
        else:
            messagebox.showwarning("Input Error", "Task description cannot be empty")

    def refresh_tasks(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
            
        priority_filter = self.filter_priority_combo.get()
        category_filter = self.filter_category_combo.get()
        status_filter = self.filter_status_combo.get()
        search_query = self.search_entry.get()

        query = "SELECT id, task, due_date, due_time, priority, category, completed, recurrence, notes FROM tasks"
        conditions = []
        if priority_filter != "All":
            conditions.append(f"priority = '{priority_filter}'")
        if category_filter != "All":
            conditions.append(f"category = '{category_filter}'")
        if status_filter != "All":
            conditions.append(f"completed = {1 if status_filter == 'Complete' else 0}")
        if search_query:
            conditions.append(f"task LIKE '%{search_query}%'")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query)
        tasks = cursor.fetchall()
        for task in tasks:
            status = "Complete" if task[6] else "Pending"
            self.task_tree.insert("", "end", values=(
                task[0], task[1], task[2], task[3], task[4], task[5], status, task[7], task[8]),
                tags=("complete" if task[6] else "pending"))
            
        self.task_tree.tag_configure("complete", background="#e8f5e9")
        self.task_tree.tag_configure("pending", background="#fffde7")

    def treeview_sort_column(self, col):
        data_type_converter = {
            "ID": int,
            "Due Date": lambda x: datetime.strptime(x, "%Y-%m-%d"),
            "Time": lambda x: datetime.strptime(x, "%H:%M").time(),
            "Priority": lambda x: {"Low": 1, "Medium": 2, "High": 3}[x],
            "Status": lambda x: {"Complete": 1, "Pending": 2}[x],
            "Task": str,
            "Category": str,
            "Recurrence": str,
            "Notes": str
        }

        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        try:
            converter = data_type_converter[col]
        except KeyError:
            converter = str

        items = [(converter(self.task_tree.set(k, col)), k) 
                for k in self.task_tree.get_children('')]

        items.sort(reverse=self.sort_reverse)

        for index, (val, k) in enumerate(items):
            self.task_tree.move(k, '', index)

        self.update_sort_arrow(col)

    def update_sort_arrow(self, col):
        for column in self.task_tree["columns"]:
            self.task_tree.heading(column, text=column)
        arrow = " ↓" if self.sort_reverse else " ↑"
        self.task_tree.heading(col, text=col + arrow)

    def complete_task(self):
        selected = self.task_tree.selection()
        if selected:
            task_id = self.task_tree.item(selected[0], "values")[0]
            cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
            conn.commit()
            self.refresh_tasks()
            messagebox.showinfo("Success", "Task marked as complete!")
        else:
            messagebox.showwarning("Selection Error", "Please select a task first")

    def edit_task(self):
        selected = self.task_tree.selection()
        if selected:
            task_id = self.task_tree.item(selected[0], "values")[0]
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            task = cursor.fetchone()

            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Task")
            edit_window.geometry("600x400")

            # Task Input
            tk.Label(edit_window, text="Task:", font=FONT_SCHEME["body"]).pack(pady=PADDING["medium"])
            task_entry = tk.Entry(edit_window, font=FONT_SCHEME["body"], width=40)
            task_entry.insert(0, task[1])
            task_entry.pack(pady=PADDING["medium"])

            # Date and Time
            datetime_frame = tk.Frame(edit_window)
            datetime_frame.pack(pady=PADDING["medium"])

            tk.Label(datetime_frame, text="Due Date:", font=FONT_SCHEME["body"]).pack(side=tk.LEFT)
            due_date_cal = DateEntry(
                datetime_frame,
                date_pattern="yyyy-mm-dd",
                font=FONT_SCHEME["body"],
                background=COLOR_SCHEME["dark"],
                foreground=COLOR_SCHEME["text"],
                borderwidth=1,
                relief=tk.FLAT
            )
            due_date_cal.set_date(datetime.strptime(task[2], "%Y-%m-%d"))
            due_date_cal.pack(side=tk.LEFT, padx=PADDING["medium"])

            tk.Label(datetime_frame, text="Time:", font=FONT_SCHEME["body"]).pack(side=tk.LEFT)
            due_time_combo = ttk.Combobox(
                datetime_frame,
                values=TIME_OPTIONS,
                font=FONT_SCHEME["body"],
                state="readonly",
                width=8
            )
            due_time_combo.set(task[3])
            due_time_combo.pack(side=tk.LEFT, padx=PADDING["medium"])

            # Priority & Category
            dropdown_frame = tk.Frame(edit_window)
            dropdown_frame.pack(pady=PADDING["medium"])

            tk.Label(dropdown_frame, text="Priority:", font=FONT_SCHEME["body"]).pack(side=tk.LEFT)
            priority_combo = ttk.Combobox(
                dropdown_frame,
                values=["Low", "Medium", "High"],
                font=FONT_SCHEME["body"],
                state="readonly",
                width=10
            )
            priority_combo.set(task[4])
            priority_combo.pack(side=tk.LEFT, padx=PADDING["medium"])

            tk.Label(dropdown_frame, text="Category:", font=FONT_SCHEME["body"]).pack(side=tk.LEFT)
            category_combo = ttk.Combobox(
                dropdown_frame,
                values=["Work", "Personal", "Shopping", "Other"],
                font=FONT_SCHEME["body"],
                state="readonly",
                width=10
            )
            category_combo.set(task[5])
            category_combo.pack(side=tk.LEFT, padx=PADDING["medium"])

            # Recurrence
            tk.Label(dropdown_frame, text="Recurrence:", font=FONT_SCHEME["body"]).pack(side=tk.LEFT)
            recurrence_combo = ttk.Combobox(
                dropdown_frame,
                values=["None", "Daily", "Weekly", "Monthly"],
                font=FONT_SCHEME["body"],
                state="readonly",
                width=10
            )
            recurrence_combo.set(task[7])
            recurrence_combo.pack(side=tk.LEFT, padx=PADDING["medium"])

            # Notes
            tk.Label(edit_window, text="Notes:", font=FONT_SCHEME["body"]).pack(pady=PADDING["medium"])
            notes_entry = tk.Text(edit_window, font=FONT_SCHEME["body"], width=40, height=4)
            notes_entry.insert("1.0", task[8])
            notes_entry.pack(pady=PADDING["medium"])

            # Save Button
            save_btn = tk.Button(edit_window, text="💾 Save Changes", 
                                command=lambda: self.save_task_changes(
                                    task_id, task_entry.get(), due_date_cal.get_date().strftime("%Y-%m-%d"),
                                    due_time_combo.get(), priority_combo.get(), category_combo.get(),
                                    recurrence_combo.get(), notes_entry.get("1.0", tk.END).strip(), edit_window
                                ),
                                bg=COLOR_SCHEME["success"], fg=COLOR_SCHEME["text"],
                                font=FONT_SCHEME["button"], relief=tk.FLAT)
            save_btn.pack(pady=PADDING["large"])

        else:
            messagebox.showwarning("Selection Error", "Please select a task to edit")

    def save_task_changes(self, task_id, task, due_date, due_time, priority, category, recurrence, notes, window):
        cursor.execute("""
            UPDATE tasks 
            SET task = ?, due_date = ?, due_time = ?, priority = ?, category = ?, recurrence = ?, notes = ?
            WHERE id = ?
        """, (task, due_date, due_time, priority, category, recurrence, notes, task_id))
        conn.commit()
        window.destroy()
        self.refresh_tasks()
        messagebox.showinfo("Success", "Task updated successfully!")

    def delete_task(self):
        selected = self.task_tree.selection()
        if selected:
            task_id = self.task_tree.item(selected[0], "values")[0]
            if messagebox.askyesno("Confirm Delete", "Delete this task permanently?"):
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
                self.refresh_tasks()
                messagebox.showinfo("Success", "Task deleted successfully!")
        else:
            messagebox.showwarning("Selection Error", "Please select a task to delete")

    def clear_all_tasks(self):
        if messagebox.askyesno("Confirm Clear", "This will delete ALL tasks!\nAre you sure?"):
            cursor.execute("DELETE FROM tasks")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
            conn.commit()
            self.refresh_tasks()
            messagebox.showinfo("Success", "All tasks cleared!")

    def export_tasks(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                                filetypes=[("CSV files", "*.csv")])
        if file_path:
            cursor.execute("SELECT * FROM tasks")
            tasks = cursor.fetchall()
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Task", "Due Date", "Due Time", "Priority", "Category", "Completed", "Recurrence", "Notes"])
                writer.writerows(tasks)
            messagebox.showinfo("Success", "Tasks exported successfully!")

    def import_tasks(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    cursor.execute("""
                        INSERT INTO tasks (task, due_date, due_time, priority, category, completed, recurrence, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (row[1], row[2], row[3], row[4], row[5], int(row[6]), row[7], row[8]))
            conn.commit()
            self.refresh_tasks()
            messagebox.showinfo("Success", "Tasks imported successfully!")

# ================= Run Application =================
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
    conn.close()