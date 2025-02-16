
tasks = []

def view_tasks():
    if not tasks:   # Check if the list is empty
        print("No Tasks Found")
    else:
        print("Your tasks: ")
        for i, task in enumerate(tasks, 1):    # Enumerate to show task numbers
            print(f"{i }. {task}")

def add_task():
    task= input("Enter your task: ")
    tasks.append(task)  # Add the task to the list
    print(f"Task '{task}' added successfully.")     
            

def complete_task():
    view_tasks()        # Show all tasks first
    try:
        task_num =int(input("Enter the task number to mark as completed: "))
        if 1<= task_num <= len(tasks):      # Check if the task number is valid
            complete_task=tasks.pop(task_num-1)
            print(f"Task '{complete_task}' marked as completed")
        else:
            print("Invalid task number. Please try again.")
    except ValueError:
        print("Please enter a valid number.")
        
def delete_task():
    view_tasks()    # Show all tasks first
    try:
        task_num =int(input("Enter the task number to delete: "))
        if 1<= task_num <= len(tasks):  # Check if the task number is valid
            deleted_task= tasks.pop(task_num-1) # Remove the task
            print(f"Task {deleted_task} deleted.")
        else:
            print("Invalid task number. Please try again.")
    except ValueError:          # Handle invalid input (non-integer)
        print("Please enter a valid number.")
        
def save_tasks():
    try:
        with open("tasks.txt", "w") as file:    # Open the file in write mode   
            for task in tasks:
                file.write(task + "\n")         # Write each task to the file
        print("Tasks saved successfully.")
    except Exception as e:                      # Catch any unexpected errors
        print(f"Error saving tasks: {e}")
def load_tasks():
    try:
        with open("tasks.txt", "r") as file:    # Open the file in read mode
            for line in file():
                tasks.append(line.strip())      # Add each task to the list
        print("Tasks loaded successfully.")
    except FileNotFoundError:
        print("No saved tasks found. Starting with an empty list.")
    except Exception as e:                      # Catch any unexpected errors
        print(f"Error saving tasks: {e}")

def show_menu():
    print("\nTo-Do App")
    print('1. View Tasks')
    print('2. Add Task')
    print('3. Mark Task as Completed') 
    print('4. Delete Task')
    print('5. Exit')
    
def main():
    load_tasks()  # Load tasks when the program starts
    while True:
        show_menu()
        #save_tasks()    # Call the save_tasks function

        choice = input("Enter your choice: ")
        if choice == '1':
            view_tasks()    # Call the view_tasks function
        elif choice == '2':
            add_task()      # Call the add_task function
        elif choice == '3':
            complete_task() # Call the complete_task function
        elif choice == '4':
            delete_task()   # Call the delete_task function
        elif choice == '5':
            save_tasks()    # Call the save_tasks function
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
if __name__ == "__main__":
    main()