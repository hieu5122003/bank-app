import tkinter as tk
from tkinter import simpledialog, messagebox
import sqlite3
from datetime import datetime

# toi la Pham Quoc Hieu
# Connect to or create the SQLite database
def create_connection():
    conn = sqlite3.connect("bank_accounts.db")
    return conn


# Create accounts and transactions tables if they don't exist
def create_table():
    conn = create_connection()
    cursor = conn.cursor()

    # Create the accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            balance REAL NOT NULL
        )
    """)

    # Create the transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_name TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            recipient TEXT
        )
    """)

    conn.commit()
    conn.close()


# Save a new account to the database
def save_account(name, balance):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO accounts (name, balance) VALUES (?, ?)", (name, balance))
    conn.commit()
    conn.close()


# Retrieve account information by name
def get_account_by_name(name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE name = ?", (name,))
    account = cursor.fetchone()
    conn.close()
    return account


# Update account balance in the database
def update_balance(name, balance):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET balance = ? WHERE name = ?", (balance, name))
    conn.commit()
    conn.close()


# Save a transaction in the transactions table
def save_transaction(account_name, transaction_type, amount, recipient=None):
    conn = create_connection()
    cursor = conn.cursor()
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "INSERT INTO transactions (account_name, transaction_type, amount, date, recipient) VALUES (?, ?, ?, ?, ?)",
        (account_name, transaction_type, amount, date, recipient))
    conn.commit()
    conn.close()


# Class BankAccount
class BankAccount:
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        else:
            return False

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        else:
            return False

    def get_balance(self):
        return self.balance

    def __str__(self):
        return f"Account holder: {self.name}, Balance: ${self.balance}"


# GUI class for BankApp
class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Banking System")
        self.account = None

        create_table()  # Initialize database tables

        # Login frame
        self.label_name_login = tk.Label(self.root, text="Enter your name:")
        self.label_name_login.grid(row=0, column=0, padx=10, pady=10)
        self.entry_name_login = tk.Entry(self.root)
        self.entry_name_login.grid(row=0, column=1, padx=10, pady=10)

        self.button_login = tk.Button(self.root, text="Login", command=self.login)
        self.button_login.grid(row=1, column=0, columnspan=2, pady=10)

        self.button_show_create_account = tk.Button(self.root, text="Create New Account",
                                                    command=self.show_create_account_form)
        self.button_show_create_account.grid(row=2, column=0, columnspan=2, pady=10)

        # Account creation frame
        self.label_name = tk.Label(self.root, text="Enter your name:")
        self.label_balance = tk.Label(self.root, text="Initial deposit ($):")
        self.entry_name = tk.Entry(self.root)
        self.entry_balance = tk.Entry(self.root)
        self.button_create_account = tk.Button(self.root, text="Create Account", command=self.create_account)

        # Transaction operations frame (only visible after login)
        self.frame_operations = tk.Frame(self.root)

        self.button_deposit = tk.Button(self.frame_operations, text="Deposit", command=self.deposit)
        self.button_withdraw = tk.Button(self.frame_operations, text="Withdraw", command=self.withdraw)
        self.button_transfer = tk.Button(self.frame_operations, text="Transfer", command=self.transfer)
        self.button_check_balance = tk.Button(self.frame_operations, text="Check Balance", command=self.check_balance)
        self.button_logout = tk.Button(self.frame_operations, text="Logout", command=self.logout)
        self.button_exit = tk.Button(self.frame_operations, text="Exit", command=self.exit_app)

        # Grid placements for transaction buttons
        self.button_deposit.grid(row=0, column=0, padx=10, pady=10)
        self.button_withdraw.grid(row=0, column=1, padx=10, pady=10)
        self.button_transfer.grid(row=1, column=0, padx=10, pady=10)
        self.button_check_balance.grid(row=1, column=1, padx=10, pady=10)
        self.button_logout.grid(row=2, column=0, padx=10, pady=10)
        self.button_exit.grid(row=2, column=1, padx=10, pady=10)

    def login(self):
        name = self.entry_name_login.get()
        account_data = get_account_by_name(name)
        if account_data:
            self.account = BankAccount(name, account_data[2])
            messagebox.showinfo("Login Successful", f"Welcome back, {name}!")
            self.label_name_login.grid_forget()
            self.entry_name_login.grid_forget()
            self.button_login.grid_forget()
            self.button_show_create_account.grid_forget()
            self.frame_operations.grid(row=3, column=0, columnspan=2)
        else:
            messagebox.showwarning("Login Failed", "Account not found. Please create a new account.")
            self.show_create_account_form()

    def show_create_account_form(self):
        # Show account creation fields
        self.label_name.grid(row=0, column=0, padx=10, pady=10)
        self.label_balance.grid(row=1, column=0, padx=10, pady=10)
        self.entry_name.grid(row=0, column=1, padx=10, pady=10)
        self.entry_balance.grid(row=1, column=1, padx=10, pady=10)
        self.button_create_account.grid(row=2, column=0, columnspan=2, pady=10)

    def create_account(self):
        name = self.entry_name.get()
        try:
            initial_balance = float(self.entry_balance.get())
            if name and initial_balance >= 0:
                existing_account = get_account_by_name(name)
                if existing_account:
                    messagebox.showwarning("Account Exists", f"Account with name {name} already exists!")
                else:
                    save_account(name, initial_balance)
                    self.account = BankAccount(name, initial_balance)
                    messagebox.showinfo("Account Created", f"Account for {name} created successfully!")
                    self.hide_create_account_form()
                    self.frame_operations.grid(row=3, column=0, columnspan=2)
            else:
                messagebox.showwarning("Invalid Input", "Please enter a valid name and initial balance.")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Initial balance must be a number.")

    def hide_create_account_form(self):
        self.label_name.grid_forget()
        self.entry_name.grid_forget()
        self.label_balance.grid_forget()
        self.entry_balance.grid_forget()
        self.button_create_account.grid_forget()

    def logout(self):
        self.account = None
        self.frame_operations.grid_forget()
        self.label_name_login.grid(row=0, column=0, padx=10, pady=10)
        self.entry_name_login.grid(row=0, column=1, padx=10, pady=10)
        self.button_login.grid(row=1, column=0, columnspan=2, pady=10)
        self.button_show_create_account.grid(row=2, column=0, columnspan=2, pady=10)
        messagebox.showinfo("Logout", "You have been logged out.")

    def deposit(self):
        if self.account:
            amount = simpledialog.askfloat("Deposit", "Enter deposit amount ($):")
            if amount and amount > 0:
                if self.account.deposit(amount):
                    update_balance(self.account.name, self.account.get_balance())
                    save_transaction(self.account.name, 'deposit', amount)
                    messagebox.showinfo("Deposit Successful",
                                        f"Deposited ${amount}. New balance: ${self.account.get_balance()}")
                else:
                    messagebox.showwarning("Deposit Error", "Invalid deposit amount.")
            else:
                messagebox.showwarning("Deposit Error", "Please enter a valid positive amount.")
        else:
            messagebox.showwarning("Account Error", "Please log in first.")
    def withdraw(self):
        if self.account:
            amount = simpledialog.askfloat("Withdraw", "Enter withdraw amount ($):")
            if amount and amount > 0:
                if self.account.withdraw(amount):
                    update_balance(self.account.name, self.account.get_balance())
                    save_transaction(self.account.name, 'withdraw', amount)
                    messagebox.showinfo("Withdrawal Successful", f"Withdrew ${amount}. New balance: ${self.account.get_balance()}")
                else:
                    messagebox.showwarning("Withdrawal Error", "Insufficient funds or invalid amount.")
            else:
                messagebox.showwarning("Withdrawal Error", "Please enter a valid positive amount.")
        else:
            messagebox.showwarning("Account Error", "Please log in first.")

    def transfer(self):
        if self.account:
            recipient = simpledialog.askstring("Transfer", "Enter recipient's name:")
            amount = simpledialog.askfloat("Transfer", "Enter transfer amount ($):")
            if recipient and amount and amount > 0:
                recipient_account = get_account_by_name(recipient)
                if recipient_account:
                    if self.account.withdraw(amount):
                        # Update sender's balance
                        update_balance(self.account.name, self.account.get_balance())
                        save_transaction(self.account.name, 'transfer_out', amount, recipient)

                        # Update recipient's balance
                        recipient_new_balance = recipient_account[2] + amount
                        update_balance(recipient, recipient_new_balance)
                        save_transaction(recipient, 'transfer_in', amount, self.account.name)

                        messagebox.showinfo("Transfer Successful", f"Transferred ${amount} to {recipient}. New balance: ${self.account.get_balance()}")
                    else:
                        messagebox.showwarning("Transfer Error", "Insufficient funds.")
                else:
                    messagebox.showwarning("Transfer Error", f"Recipient account '{recipient}' does not exist.")
            else:
                messagebox.showwarning("Transfer Error", "Please enter a valid recipient and amount.")
        else:
            messagebox.showwarning("Account Error", "Please log in first.")

    def check_balance(self):
        if self.account:
            messagebox.showinfo("Account Balance", f"Your balance: ${self.account.get_balance()}")
        else:
            messagebox.showwarning("Account Error", "Please log in first.")

    def exit_app(self):
        self.root.quit()

    # Remaining methods (withdraw, transfer, check_balance, exit_app) remain the same
    # ...


# Create the main window
root = tk.Tk()

# Create an instance of BankApp
app = BankApp(root)

# Start the GUI event loop
root.mainloop()