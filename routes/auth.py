from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import register_user, login_user

auth = Blueprint('auth', __name__)


# ─────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────

def login_required(f):
    """Decorator to protect routes that need login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# ─────────────────────────────────────────
# REGISTER
# ─────────────────────────────────────────

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # If already logged in redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        success, messages = register_user(username, email, password, confirm_password)

        if success:
            flash(messages[0], "success")
            return redirect(url_for('auth.login'))
        else:
            for msg in messages:
                flash(msg, "danger")
            return render_template('register.html',
                                   username=username,
                                   email=email)

    return render_template('register.html')


# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        success, messages, user_data = login_user(email, password)

        if success:
            # Store user info in session
            session['user_id'] = user_data['id']
            session['username'] = user_data['username']
            session['email'] = user_data['email']
            flash(messages[0], "success")
            return redirect(url_for('dashboard.index'))
        else:
            for msg in messages:
                flash(msg, "danger")
            return render_template('login.html', email=email)

    return render_template('login.html')


# ─────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────

@auth.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('auth.login'))