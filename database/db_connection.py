import sqlite3
import os

# Database will be created in the database/ folder
DB_PATH = os.path.join(os.path.dirname(__file__), 'pfms.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            user_id INTEGER,
            is_default INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            note TEXT,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')

    # Insert default categories
    default_income = ['Salary', 'Business', 'Investment', 'Freelance', 'Other Income']
    default_expense = ['Rent', 'Groceries', 'Food', 'Transport', 'Entertainment',
                       'Healthcare', 'Education', 'Shopping', 'Utilities', 'Other Expense']

    for cat in default_income:
        cursor.execute('''
            INSERT OR IGNORE INTO categories (name, type, user_id, is_default)
            VALUES (?, 'income', NULL, 1)
        ''', (cat,))

    for cat in default_expense:
        cursor.execute('''
            INSERT OR IGNORE INTO categories (name, type, user_id, is_default)
            VALUES (?, 'expense', NULL, 1)
        ''', (cat,))

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

if __name__ == '__main__':
    init_db()