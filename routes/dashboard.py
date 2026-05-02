from flask import Blueprint, render_template, session, jsonify
from routes.auth import login_required
from models.transaction import (
    get_summary,
    get_all_transactions,
    get_category_breakdown,
    get_monthly_data
)

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/')
@login_required
def index():
    user_id = session['user_id']

    # Get summary data
    summary = get_summary(user_id)

    # Get recent 5 transactions
    all_transactions = get_all_transactions(user_id)
    recent_transactions = all_transactions[:5]

    # Get category breakdown for pie chart
    category_breakdown = get_category_breakdown(user_id)

    # Get monthly data for bar chart
    monthly_data = get_monthly_data(user_id)

    # Prepare chart data
    pie_labels = [c['category'] for c in category_breakdown]
    pie_values = [c['total'] for c in category_breakdown]

    months = sorted(monthly_data.keys())[-6:]  # last 6 months
    bar_labels = months
    bar_income = [monthly_data.get(m, {}).get('income', 0) for m in months]
    bar_expense = [monthly_data.get(m, {}).get('expense', 0) for m in months]

    return render_template('dashboard.html',
                           username=session['username'],
                           summary=summary,
                           recent_transactions=recent_transactions,
                           pie_labels=pie_labels,
                           pie_values=pie_values,
                           bar_labels=bar_labels,
                           bar_income=bar_income,
                           bar_expense=bar_expense)


# ─────────────────────────────────────────
# API ENDPOINTS FOR CHART.JS
# ─────────────────────────────────────────

@dashboard.route('/api/summary')
@login_required
def api_summary():
    user_id = session['user_id']
    return jsonify(get_summary(user_id))

@dashboard.route('/api/category-breakdown')
@login_required
def api_category_breakdown():
    user_id = session['user_id']
    return jsonify(get_category_breakdown(user_id))

@dashboard.route('/api/monthly-data')
@login_required
def api_monthly_data():
    user_id = session['user_id']
    return jsonify(get_monthly_data(user_id))