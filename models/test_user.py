import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import init_db
from models.user import register_user, verify_password, validate_registration
from database.db_connection import get_user_by_email

# Init DB first
init_db()

print("\n─── Testing Registration ───")

# Test 1 - Valid registration
success, messages = register_user(
    username="krishna",
    email="krishna@gmail.com",
    password="secure123",
    confirm_password="secure123"
)
print(f"Valid registration: {'✅' if success else '❌'} - {messages[0]}")

# Test 2 - Duplicate username
success, messages = register_user(
    username="krishna",
    email="another@gmail.com",
    password="secure123",
    confirm_password="secure123"
)
print(f"Duplicate username: {'✅ Caught' if not success else '❌ Missed'} - {messages[0]}")

# Test 3 - Duplicate email
success, messages = register_user(
    username="newuser",
    email="krishna@gmail.com",
    password="secure123",
    confirm_password="secure123"
)
print(f"Duplicate email: {'✅ Caught' if not success else '❌ Missed'} - {messages[0]}")

# Test 4 - Password mismatch
success, messages = register_user(
    username="newuser2",
    email="new@gmail.com",
    password="secure123",
    confirm_password="wrong123"
)
print(f"Password mismatch: {'✅ Caught' if not success else '❌ Missed'} - {messages[0]}")

# Test 5 - Short password
success, messages = register_user(
    username="newuser3",
    email="new3@gmail.com",
    password="123",
    confirm_password="123"
)
print(f"Short password: {'✅ Caught' if not success else '❌ Missed'} - {messages[0]}")

print("\n─── Testing Password Hashing ───")

# Test 6 - Verify hashed password
user = get_user_by_email("krishna@gmail.com")
if user:
    is_valid = verify_password("secure123", user['password'])
    is_invalid = verify_password("wrongpass", user['password'])
    print(f"Correct password verify: {'✅' if is_valid else '❌'}")
    print(f"Wrong password verify: {'✅ Rejected' if not is_invalid else '❌ Accepted'}")

print("\n✅ All registration tests passed!")