from database.db_connection import (
    insert_transaction,
    get_categories_by_type,
    insert_custom_category,
    get_transactions_by_user,
    get_transactions_by_date_range,
    get_total_income,
    get_total_expense,
    get_expense_by_category,
    get_monthly_summary
)


# ─────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────

def validate_transaction(amount, category_id, date, note):
    errors = []

    # Amount validation
    try:
        amount = float(amount)
        if amount <= 0:
            errors.append("Amount must be greater than 0.")
        if amount > 10000000:
            errors.append("Amount cannot exceed 1 crore.")
    except (ValueError, TypeError):
        errors.append("Please enter a valid amount.")

    # Category validation
    if not category_id:
        errors.append("Please select a category.")

    # Date validation
    if not date:
        errors.append("Please select a date.")
    else:
        from datetime import datetime
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid date format.")

    # Note validation
    if note and len(note) > 200:
        errors.append("Note cannot exceed 200 characters.")

    return errors


# ─────────────────────────────────────────
# INCOME
# ─────────────────────────────────────────

def add_income(user_id, category_id, amount, note, date):
    """
    Full income transaction flow:
    1. Validate inputs
    2. Insert transaction
    """

    # Step 1 - Validate
    errors = validate_transaction(amount, category_id, date, note)
    if errors:
        return False, errors

    # Step 2 - Insert
    try:
        amount = float(amount)
        insert_transaction(
            user_id=user_id,
            category_id=int(category_id),
            amount=amount,
            type='income',
            note=note.strip() if note else '',
            date=date
        )
        return True, ["Income added successfully! 💰"]
    except Exception as e:
        return False, [f"Failed to add income: {str(e)}"]


# ─────────────────────────────────────────
# EXPENSE
# ─────────────────────────────────────────

def add_expense(user_id, category_id, amount, note, date):
    """
    Full expense transaction flow:
    1. Validate inputs
    2. Insert transaction
    """

    # Step 1 - Validate
    errors = validate_transaction(amount, category_id, date, note)
    if errors:
        return False, errors

    # Step 2 - Insert
    try:
        amount = float(amount)
        insert_transaction(
            user_id=user_id,
            category_id=int(category_id),
            amount=amount,
            type='expense',
            note=note.strip() if note else '',
            date=date
        )
        return True, ["Expense added successfully! 💸"]
    except Exception as e:
        return False, [f"Failed to add expense: {str(e)}"]

# ─────────────────────────────────────────
# CATEGORIES
# ─────────────────────────────────────────

def get_income_categories(user_id):
    """Get all income categories for a user"""
    categories = get_categories_by_type('income', user_id)
    return [{'id': c['id'], 'name': c['name']} for c in categories]

def get_expense_categories(user_id):
    """Get all expense categories for a user"""
    categories = get_categories_by_type('expense', user_id)
    return [{'id': c['id'], 'name': c['name']} for c in categories]

def add_custom_category(name, type, user_id):
    """Add a custom category for a user"""
    errors = []

    if not name or len(name.strip()) < 2:
        errors.append("Category name must be at least 2 characters.")
    if len(name) > 30:
        errors.append("Category name cannot exceed 30 characters.")
    if type not in ['income', 'expense']:
        errors.append("Invalid category type.")

    if errors:
        return False, errors

    success = insert_custom_category(name.strip(), type, user_id)
    if success:
        return True, ["Category added successfully!"]
    return False, ["Category already exists."]


# ─────────────────────────────────────────
# FETCH TRANSACTIONS
# ─────────────────────────────────────────

def get_all_transactions(user_id):
    """Get all transactions for a user"""
    transactions = get_transactions_by_user(user_id)
    return [dict(t) for t in transactions]

def get_transactions_by_range(user_id, start_date, end_date):
    """Get transactions between two dates"""
    transactions = get_transactions_by_date_range(user_id, start_date, end_date)
    return [dict(t) for t in transactions]


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────

def get_summary(user_id):
    """Get financial summary for a user"""
    total_income = get_total_income(user_id)
    total_expense = get_total_expense(user_id)
    balance = total_income - total_expense

    return {
        'total_income': round(total_income, 2),
        'total_expense': round(total_expense, 2),
        'balance': round(balance, 2),
        'savings_rate': round((balance / total_income * 100), 2) if total_income > 0 else 0
    }

def get_category_breakdown(user_id):
    """Get expense breakdown by category"""
    results = get_expense_by_category(user_id)
    return [{'category': r['category'], 'total': round(r['total'], 2)} for r in results]

def get_monthly_data(user_id):
    """Get monthly income vs expense data"""
    results = get_monthly_summary(user_id)
    monthly = {}
    for row in results:
        month = row['month']
        if month not in monthly:
            monthly[month] = {'income': 0, 'expense': 0}
        monthly[month][row['type']] = round(row['total'], 2)
    return monthly

# ─────────────────────────────────────────
# UPDATE & DELETE
# ─────────────────────────────────────────

def delete_transaction_by_id(transaction_id, user_id):
    """Delete a transaction by ID"""
    from database.db_connection import delete_transaction
    try:
        delete_transaction(transaction_id, user_id)
        return True, ["Transaction deleted successfully!"]
    except Exception as e:
        return False, [f"Failed to delete: {str(e)}"]

def update_transaction_by_id(transaction_id, user_id, category_id, amount, type, note, date):
    """Update a transaction by ID"""
    from database.db_connection import update_transaction
    errors = validate_transaction(amount, category_id, date, note)
    if errors:
        return False, errors
    try:
        update_transaction(
            transaction_id=transaction_id,
            user_id=user_id,
            category_id=int(category_id),
            amount=float(amount),
            type=type,
            note=note.strip() if note else '',
            date=date
        )
        return True, ["Transaction updated successfully!"]
    except Exception as e:
        return False, [f"Failed to update: {str(e)}"]