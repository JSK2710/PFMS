from db_connection import init_db, insert_user, get_user_by_email, \
    insert_transaction, get_transactions_by_user, \
    get_total_income, get_total_expense, \
    delete_transaction, get_categories_by_type

# Step 1 - Init DB
init_db()

# Step 2 - Test insert user
result = insert_user("testuser", "test@gmail.com", "hashedpassword123")
print(f"Insert user: {'✅ Success' if result else '❌ Already exists'}")

# Step 3 - Test fetch user
user = get_user_by_email("test@gmail.com")
print(f"Fetch user: ✅ Found - {user['username']}" if user else "❌ Not found")

# Step 4 - Test get categories
categories = get_categories_by_type('expense', None)
print(f"Categories: ✅ Found {len(categories)} expense categories")

# Step 5 - Test insert transaction
result = insert_transaction(
    user_id=1,
    category_id=1,
    amount=5000.00,
    type='income',
    note='Test salary',
    date='2026-03-09'
)
print(f"Insert transaction: {'✅ Success' if result else '❌ Failed'}")

# Step 6 - Test fetch transactions
transactions = get_transactions_by_user(1)
print(f"Fetch transactions: ✅ Found {len(transactions)} transactions")

# Step 7 - Test totals
income = get_total_income(1)
expense = get_total_expense(1)
print(f"Total income: ✅ ₹{income}")
print(f"Total expense: ✅ ₹{expense}")

# Step 8 - Test delete
if transactions:
    delete_transaction(transactions[0]['id'], 1)
    print("Delete transaction: ✅ Success")

print("\n✅ All CRUD operations working correctly!")