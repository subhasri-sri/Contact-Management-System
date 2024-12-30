import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sqlite3
import csv

# Database setup
def init_db():
    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        email TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL
                    )''')
    conn.commit()
    conn.close()

# User authentication functions
def login_user():
    username = username_entry.get()
    password = password_entry.get()

    if username == "" or password == "":
        messagebox.showerror("Login Error", "All fields are required!")
        return

    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        messagebox.showinfo("Login Successful", f"Welcome {username}!")
        login_frame.pack_forget()
        main_frame.pack()
        load_contacts()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def register_user():
    username = username_entry.get()
    password = password_entry.get()

    if username == "" or password == "":
        messagebox.showerror("Registration Error", "All fields are required!")
        return

    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        messagebox.showinfo("Registration Successful", "You can now log in.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Registration Error", "Username already exists.")
    finally:
        conn.close()

# Functions
def add_contact():
    name = name_entry.get()
    phone = phone_entry.get()
    email = email_entry.get()

    if name == "" or phone == "":
        messagebox.showerror("Input Error", "Name and Phone fields are mandatory!")
        return

    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)", (name, phone, email))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Contact added successfully!")
    clear_entries()
    load_contacts()

def load_contacts():
    for row in contact_tree.get_children():
        contact_tree.delete(row)

    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts")
    rows = cursor.fetchall()
    for row in rows:
        contact_tree.insert("", "end", values=row)
    conn.close()

def delete_contact():
    selected_item = contact_tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "Please select a contact to delete!")
        return

    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this contact?")
    if confirm:
        conn = sqlite3.connect("contacts.db")
        cursor = conn.cursor()
        for item in selected_item:
            contact_id = contact_tree.item(item, "values")[0]
            cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        conn.commit()
        conn.close()
        load_contacts()

def update_contact():
    selected_item = contact_tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "Please select a contact to update!")
        return

    contact_id = contact_tree.item(selected_item[0], "values")[0]
    name = name_entry.get()
    phone = phone_entry.get()
    email = email_entry.get()

    if name == "" or phone == "":
        messagebox.showerror("Input Error", "Name and Phone fields are mandatory!")
        return

    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE contacts SET name = ?, phone = ?, email = ? WHERE id = ?", (name, phone, email, contact_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Contact updated successfully!")
    clear_entries()
    load_contacts()

def clear_entries():
    name_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)

def populate_entries(event):
    selected_item = contact_tree.selection()
    if not selected_item:
        return

    contact_id, name, phone, email = contact_tree.item(selected_item[0], "values")
    name_entry.delete(0, tk.END)
    name_entry.insert(0, name)
    phone_entry.delete(0, tk.END)
    phone_entry.insert(0, phone)
    email_entry.delete(0, tk.END)
    email_entry.insert(0, email)

def search_contacts():
    query = search_entry.get()
    for row in contact_tree.get_children():
        contact_tree.delete(row)

    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?", (f"%{query}%", f"%{query}%", f"%{query}%"))
    rows = cursor.fetchall()
    for row in rows:
        contact_tree.insert("", "end", values=row)
    conn.close()

def sort_contacts(column):
    for row in contact_tree.get_children():
        contact_tree.delete(row)

    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM contacts ORDER BY {column}")
    rows = cursor.fetchall()
    for row in rows:
        contact_tree.insert("", "end", values=row)
    conn.close()

def backup_contacts():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts")
    rows = cursor.fetchall()
    conn.close()

    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Name", "Phone", "Email"])
        writer.writerows(rows)

    messagebox.showinfo("Backup Successful", "Contacts have been backed up successfully!")

def restore_contacts():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    conn = sqlite3.connect("contacts.db")
    cursor = conn.cursor()

    with open(file_path, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            cursor.execute("INSERT OR IGNORE INTO contacts (id, name, phone, email) VALUES (?, ?, ?, ?)", (row[0], row[1], row[2], row[3]))

    conn.commit()
    conn.close()
    load_contacts()
    messagebox.showinfo("Restore Successful", "Contacts have been restored successfully!")

# Initialize database
init_db()

# GUI Setup
root = tk.Tk()
root.title("Contact Management System")
root.geometry("600x400")

# Login frame
login_frame = tk.Frame(root)
login_frame.pack()

login_label = tk.Label(login_frame, text="Login to Contact Management System")
login_label.pack(pady=10)

username_label = tk.Label(login_frame, text="Username:")
username_label.pack()
username_entry = tk.Entry(login_frame)
username_entry.pack()

password_label = tk.Label(login_frame, text="Password:")
password_label.pack()
password_entry = tk.Entry(login_frame, show="*")
password_entry.pack()

login_button = tk.Button(login_frame, text="Login", command=login_user)
login_button.pack(pady=5)

register_button = tk.Button(login_frame, text="Register", command=register_user)
register_button.pack()

# Main frame
main_frame = tk.Frame(root)

# Search bar
search_frame = tk.Frame(main_frame)
search_frame.pack(pady=10)

search_label = tk.Label(search_frame, text="Search:")
search_label.grid(row=0, column=0, padx=5)
search_entry = tk.Entry(search_frame)
search_entry.grid(row=0, column=1, padx=5)
search_button = tk.Button(search_frame, text="Search", command=search_contacts)
search_button.grid(row=0, column=2, padx=5)

# Sort buttons
sort_frame = tk.Frame(main_frame)
sort_frame.pack(pady=10)

sort_name_button = tk.Button(sort_frame, text="Sort by Name", command=lambda: sort_contacts("name"))
sort_name_button.grid(row=0, column=0, padx=5)

sort_phone_button = tk.Button(sort_frame, text="Sort by Phone", command=lambda: sort_contacts("phone"))
sort_phone_button.grid(row=0, column=1, padx=5)

sort_email_button = tk.Button(sort_frame, text="Sort by Email", command=lambda: sort_contacts("email"))
sort_email_button.grid(row=0, column=2, padx=5)

# Form frame
form_frame = tk.Frame(main_frame)
form_frame.pack(pady=10)

name_label = tk.Label(form_frame, text="Name:")
name_label.grid(row=0, column=0, padx=5, pady=5)
name_entry = tk.Entry(form_frame)
name_entry.grid(row=0, column=1, padx=5, pady=5)

phone_label = tk.Label(form_frame, text="Phone:")
phone_label.grid(row=1, column=0, padx=5, pady=5)
phone_entry = tk.Entry(form_frame)
phone_entry.grid(row=1, column=1, padx=5, pady=5)

email_label = tk.Label(form_frame, text="Email:")
email_label.grid(row=2, column=0, padx=5, pady=5)
email_entry = tk.Entry(form_frame)
email_entry.grid(row=2, column=1, padx=5, pady=5)

button_frame = tk.Frame(main_frame)
button_frame.pack(pady=10)

add_button = tk.Button(button_frame, text="Add Contact", command=add_contact)
add_button.grid(row=0, column=0, padx=5)

delete_button = tk.Button(button_frame, text="Delete Contact", command=delete_contact)
delete_button.grid(row=0, column=1, padx=5)

update_button = tk.Button(button_frame, text="Update Contact", command=update_contact)
update_button.grid(row=0, column=2, padx=5)

clear_button = tk.Button(button_frame, text="Clear Fields", command=clear_entries)
clear_button.grid(row=0, column=3, padx=5)

backup_button = tk.Button(button_frame, text="Backup Contacts", command=backup_contacts)
backup_button.grid(row=0, column=4, padx=5)

restore_button = tk.Button(button_frame, text="Restore Contacts", command=restore_contacts)
restore_button.grid(row=0, column=5, padx=5)

# Contact list frame
list_frame = tk.Frame(main_frame)
list_frame.pack(pady=10)

columns = ("id", "name", "phone", "email")
contact_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
contact_tree.heading("id", text="ID")
contact_tree.heading("name", text="Name")
contact_tree.heading("phone", text="Phone")
contact_tree.heading("email", text="Email")

contact_tree.column("id", width=30)
contact_tree.column("name", width=150)
contact_tree.column("phone", width=100)
contact_tree.column("email", width=150)

contact_tree.pack(fill=tk.BOTH, expand=True)

contact_tree.bind("<ButtonRelease-1>", populate_entries)

# Run the app
root.mainloop()
