import bcrypt
from database.db_connection import (
    insert_user,
    get_user_by_email,
    get_user_by_username,
    get_user_by_id
)


# ─────────────────────────────────────────
# PASSWORD HASHING
# ─────────────────────────────────────────

def hash_password(password):
    """Hash a plain text password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def verify_password(plain_password, hashed_password):
    """Verify a plain password against a hashed password"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password
    )


# ─────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────

def validate_registration(username, email, password, confirm_password):
    """Validate registration form inputs"""
    errors = []

    # Username validation
    if not username or len(username.strip()) < 3:
        errors.append("Username must be at least 3 characters.")
    if len(username) > 20:
        errors.append("Username must be less than 20 characters.")
    if not username.isalnum():
        errors.append("Username can only contain letters and numbers.")

    # Email validation
    if not email or '@' not in email or '.' not in email:
        errors.append("Please enter a valid email address.")

    # Password validation
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters.")
    if password != confirm_password:
        errors.append("Passwords do not match.")

    return errors

def validate_login(email, password):
    """Validate login form inputs"""
    errors = []

    if not email or '@' not in email:
        errors.append("Please enter a valid email address.")
    if not password:
        errors.append("Please enter your password.")

    return errors


# ─────────────────────────────────────────
# REGISTRATION
# ─────────────────────────────────────────

def register_user(username, email, password, confirm_password):
    """
    Full registration flow:
    1. Validate inputs
    2. Check if user already exists
    3. Hash password
    4. Insert into database
    """

    # Step 1 - Validate inputs
    errors = validate_registration(username, email, password, confirm_password)
    if errors:
        return False, errors

    # Step 2 - Check if username already exists
    existing_username = get_user_by_username(username)
    if existing_username:
        return False, ["Username already taken. Please choose another."]

    # Step 3 - Check if email already exists
    existing_email = get_user_by_email(email)
    if existing_email:
        return False, ["Email already registered. Please login instead."]

    # Step 4 - Hash password
    hashed_password = hash_password(password)

    # Step 5 - Insert user into database
    success = insert_user(username, email, hashed_password)
    if success:
        return True, ["Registration successful! Please login."]
    else:
        return False, ["Registration failed. Please try again."]


# ─────────────────────────────────────────
# FETCH USER
# ─────────────────────────────────────────

def get_user(user_id):
    """Get user details by ID"""
    user = get_user_by_id(user_id)
    if user:
        return {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'created_at': user['created_at']
        }
    return None

# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────

def login_user(email, password):
    """
    Full login flow:
    1. Validate inputs
    2. Check if user exists
    3. Verify password
    4. Return user data
    """

    # Step 1 - Validate inputs
    errors = validate_login(email, password)
    if errors:
        return False, errors, None

    # Step 2 - Check if user exists
    user = get_user_by_email(email)
    if not user:
        return False, ["No account found with this email."], None

    # Step 3 - Verify password
    if not verify_password(password, user['password']):
        return False, ["Incorrect password. Please try again."], None

    # Step 4 - Return user data
    user_data = {
        'id': user['id'],
        'username': user['username'],
        'email': user['email']
    }
    return True, ["Login successful!"], user_data