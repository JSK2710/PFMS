from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from routes.auth import login_required
from models.transaction import (
    add_income,
    get_income_categories,
    add_custom_category
)
from datetime import date

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