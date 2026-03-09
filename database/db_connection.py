import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'pfms.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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


# ─────────────────────────────────────────
# USER CRUD
# ─────────────────────────────────────────

def insert_user(username, email, hashed_password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        ''', (username, email, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # username or email already exists
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


# ─────────────────────────────────────────
# CATEGORY CRUD
# ─────────────────────────────────────────

def get_categories_by_type(type, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM categories
        WHERE type = ?
        AND (is_default = 1 OR user_id = ?)
    ''', (type, user_id))
    categories = cursor.fetchall()
    conn.close()
    return categories

def insert_custom_category(name, type, user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO categories (name, type, user_id, is_default)
            VALUES (?, ?, ?, 0)
        ''', (name, type, user_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


# ─────────────────────────────────────────
# TRANSACTION CRUD
# ─────────────────────────────────────────

def insert_transaction(user_id, category_id, amount, type, note, date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (user_id, category_id, amount, type, note, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, category_id, amount, type, note, date))
    conn.commit()
    conn.close()
    return True

def get_transactions_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.*, c.name as category_name
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
        ORDER BY t.date DESC
    ''', (user_id,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def get_transactions_by_date_range(user_id, start_date, end_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.*, c.name as category_name
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
        AND t.date BETWEEN ? AND ?
        ORDER BY t.date DESC
    ''', (user_id, start_date, end_date))
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def update_transaction(transaction_id, user_id, category_id, amount, type, note, date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE transactions
        SET category_id = ?, amount = ?, type = ?, note = ?, date = ?
        WHERE id = ? AND user_id = ?
    ''', (category_id, amount, type, note, date, transaction_id, user_id))
    conn.commit()
    conn.close()
    return True

def delete_transaction(transaction_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM transactions
        WHERE id = ? AND user_id = ?
    ''', (transaction_id, user_id))
    conn.commit()
    conn.close()
    return True


# ─────────────────────────────────────────
# SUMMARY QUERIES
# ─────────────────────────────────────────

def get_total_income(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) as total
        FROM transactions
        WHERE user_id = ? AND type = 'income'
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result['total']

def get_total_expense(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) as total
        FROM transactions
        WHERE user_id = ? AND type = 'expense'
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result['total']

def get_expense_by_category(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.name as category, COALESCE(SUM(t.amount), 0) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND t.type = 'expense'
        GROUP BY c.name
        ORDER BY total DESC
    ''', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_monthly_summary(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            strftime('%Y-%m', date) as month,
            type,
            COALESCE(SUM(amount), 0) as total
        FROM transactions
        WHERE user_id = ?
        GROUP BY month, type
        ORDER BY month DESC
    ''', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results