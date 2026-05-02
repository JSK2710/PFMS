from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from routes.auth import login_required
from models.transaction import (
    add_income,
    add_expense,
    get_income_categories,
    get_expense_categories,
    get_all_transactions,
    get_transactions_by_range,
    get_summary,
    add_custom_category,
    delete_transaction_by_id,
    update_transaction_by_id
)
from datetime import date, datetime, timedelta

transactions = Blueprint('transactions', __name__)


# ─────────────────────────────────────────
# ADD INCOME
# ─────────────────────────────────────────

@transactions.route('/add-income', methods=['GET', 'POST'])
@login_required
def add_income_route():
    user_id = session['user_id']
    categories = get_income_categories(user_id)
    today = date.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        category_id = request.form.get('category_id')
        amount = request.form.get('amount')
        note = request.form.get('note', '')
        date_input = request.form.get('date')

        success, messages = add_income(
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            note=note,
            date=date_input
        )

        if success:
            flash(messages[0], "success")
            return redirect(url_for('transactions.add_income_route'))
        else:
            for msg in messages:
                flash(msg, "danger")
            return render_template('add_income.html',
                                   categories=categories,
                                   today=today,
                                   form_data=request.form)

    return render_template('add_income.html',
                           categories=categories,
                           today=today)


# ─────────────────────────────────────────
# ADD CUSTOM CATEGORY
# ─────────────────────────────────────────

@transactions.route('/add-category', methods=['POST'])
@login_required
def add_category():
    user_id = session['user_id']
    name = request.form.get('name', '')
    type = request.form.get('type', '')

    success, messages = add_custom_category(name, type, user_id)

    if success:
        flash(messages[0], "success")
    else:
        flash(messages[0], "danger")

    # Redirect back to the page that made the request
    return redirect(request.referrer or url_for('transactions.add_income_route'))

# ─────────────────────────────────────────
# ADD EXPENSE
# ─────────────────────────────────────────

@transactions.route('/add-expense', methods=['GET', 'POST'])
@login_required
def add_expense_route():
    user_id = session['user_id']
    categories = get_expense_categories(user_id)
    today = date.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        category_id = request.form.get('category_id')
        amount = request.form.get('amount')
        note = request.form.get('note', '')
        date_input = request.form.get('date')

        success, messages = add_expense(
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            note=note,
            date=date_input
        )

        if success:
            flash(messages[0], "success")
            return redirect(url_for('transactions.add_expense_route'))
        else:
            for msg in messages:
                flash(msg, "danger")
            return render_template('add_expense.html',
                                   categories=categories,
                                   today=today,
                                   form_data=request.form)

    return render_template('add_expense.html',
                           categories=categories,
                           today=today)

# ─────────────────────────────────────────
# TRANSACTION HISTORY
# ─────────────────────────────────────────

@transactions.route('/history')
@login_required
def history():
    user_id = session['user_id']

    # Get filter params from URL
    filter_type = request.args.get('type', 'all')        # all, income, expense
    filter_range = request.args.get('range', 'all')      # all, today, week, month, custom
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    today = date.today()

    # Calculate date range based on filter
    if filter_range == 'today':
        start_date = today.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif filter_range == 'week':
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif filter_range == 'month':
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif filter_range == 'custom' and start_date and end_date:
        pass  # use dates from URL params
    else:
        start_date = ''
        end_date = ''

    # Fetch transactions
    if start_date and end_date:
        all_transactions = get_transactions_by_range(user_id, start_date, end_date)
    else:
        all_transactions = get_all_transactions(user_id)

    # Filter by type
    if filter_type == 'income':
        all_transactions = [t for t in all_transactions if t['type'] == 'income']
    elif filter_type == 'expense':
        all_transactions = [t for t in all_transactions if t['type'] == 'expense']

    # Get summary
    summary = get_summary(user_id)

    return render_template('history.html',
                           transactions=all_transactions,
                           summary=summary,
                           filter_type=filter_type,
                           filter_range=filter_range,
                           start_date=start_date,
                           end_date=end_date,
                           today=today.strftime('%Y-%m-%d'))


# ─────────────────────────────────────────
# DELETE TRANSACTION
# ─────────────────────────────────────────

@transactions.route('/delete-transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction_route(transaction_id):
    user_id = session['user_id']
    success, messages = delete_transaction_by_id(transaction_id, user_id)

    if success:
        flash(messages[0], "success")
    else:
        flash(messages[0], "danger")

    return redirect(url_for('transactions.history'))


# ─────────────────────────────────────────
# EDIT TRANSACTION
# ─────────────────────────────────────────

@transactions.route('/edit-transaction/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction_route(transaction_id):
    user_id = session['user_id']
    today = date.today().strftime('%Y-%m-%d')

    # Get the transaction
    all_transactions = get_all_transactions(user_id)
    transaction = next((t for t in all_transactions if t['id'] == transaction_id), None)

    if not transaction:
        flash("Transaction not found.", "danger")
        return redirect(url_for('transactions.history'))

    # Get categories based on type
    if transaction['type'] == 'income':
        categories = get_income_categories(user_id)
    else:
        categories = get_expense_categories(user_id)

    if request.method == 'POST':
        category_id = request.form.get('category_id')
        amount = request.form.get('amount')
        note = request.form.get('note', '')
        date_input = request.form.get('date')

        success, messages = update_transaction_by_id(
            transaction_id=transaction_id,
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            type=transaction['type'],
            note=note,
            date=date_input
        )

        if success:
            flash(messages[0], "success")
            return redirect(url_for('transactions.history'))
        else:
            for msg in messages:
                flash(msg, "danger")

    return render_template('edit_transaction.html',
                           transaction=transaction,
                           categories=categories,
                           today=today)