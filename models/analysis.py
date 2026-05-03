import pandas as pd
from database.db_connection import get_connection


# ─────────────────────────────────────────
# FETCH DATA
# ─────────────────────────────────────────

def get_transactions_df(user_id):
    """Load all transactions into a Pandas DataFrame"""
    conn = get_connection()
    query = '''
        SELECT 
            t.id,
            t.amount,
            t.type,
            t.date,
            t.note,
            c.name as category
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
        ORDER BY t.date DESC
    '''
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()

    if df.empty:
        return df

    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%Y-%m')
    df['month_name'] = df['date'].dt.strftime('%B %Y')

    return df


# ─────────────────────────────────────────
# SPENDING ANALYSIS
# ─────────────────────────────────────────

def get_spending_analysis(user_id):
    """
    Full spending analysis using Pandas:
    - Total income & expense
    - Savings rate
    - Category breakdown with percentages
    - Monthly trends
    - Top spending category
    - Average daily spending
    """
    df = get_transactions_df(user_id)

    if df.empty:
        return {
            'has_data': False,
            'message': 'No transactions found. Add some transactions to see analysis.'
        }

    income_df = df[df['type'] == 'income']
    expense_df = df[df['type'] == 'expense']

    total_income = round(income_df['amount'].sum(), 2)
    total_expense = round(expense_df['amount'].sum(), 2)
    balance = round(total_income - total_expense, 2)
    savings_rate = round((balance / total_income * 100), 2) if total_income > 0 else 0


    # ── Category Breakdown ──
    if not expense_df.empty:
        category_group = expense_df.groupby('category')['amount'].sum().reset_index()
        category_group.columns = ['category', 'total']
        category_group = category_group.sort_values('total', ascending=False)
        category_group['percentage'] = round(
            (category_group['total'] / total_expense * 100), 1
        )
        category_breakdown = category_group.to_dict('records')
        top_category = category_group.iloc[0]['category']
        top_category_amount = round(category_group.iloc[0]['total'], 2)
        top_category_pct = round(category_group.iloc[0]['percentage'], 1)
    else:
        category_breakdown = []
        top_category = None
        top_category_amount = 0
        top_category_pct = 0


    # ── Monthly Trends ──
    if not df.empty:
        monthly_income = income_df.groupby('month')['amount'].sum()
        monthly_expense = expense_df.groupby('month')['amount'].sum()
        all_months = sorted(set(
            list(monthly_income.index) + list(monthly_expense.index)
        ))[-6:]  # last 6 months

        monthly_trends = []
        for month in all_months:
            inc = round(monthly_income.get(month, 0), 2)
            exp = round(monthly_expense.get(month, 0), 2)
            monthly_trends.append({
                'month': month,
                'income': inc,
                'expense': exp,
                'balance': round(inc - exp, 2)
            })
    else:
        monthly_trends = []


    # ── Average Daily Spending ──
    if not expense_df.empty:
        date_range = (df['date'].max() - df['date'].min()).days + 1
        avg_daily_expense = round(total_expense / max(date_range, 1), 2)
        avg_monthly_expense = round(total_expense / max(len(expense_df['month'].unique()), 1), 2)
    else:
        avg_daily_expense = 0
        avg_monthly_expense = 0


    # ── Transaction Count ──
    total_transactions = len(df)
    income_count = len(income_df)
    expense_count = len(expense_df)


    # ── Most Active Month ──
    if not expense_df.empty:
        monthly_exp_total = expense_df.groupby('month')['amount'].sum()
        most_active_month = monthly_exp_total.idxmax()
        most_active_month_amount = round(monthly_exp_total.max(), 2)
    else:
        most_active_month = None
        most_active_month_amount = 0

    return {
        'has_data': True,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'savings_rate': savings_rate,
        'category_breakdown': category_breakdown,
        'top_category': top_category,
        'top_category_amount': top_category_amount,
        'top_category_pct': top_category_pct,
        'monthly_trends': monthly_trends,
        'avg_daily_expense': avg_daily_expense,
        'avg_monthly_expense': avg_monthly_expense,
        'total_transactions': total_transactions,
        'income_count': income_count,
        'expense_count': expense_count,
        'most_active_month': most_active_month,
        'most_active_month_amount': most_active_month_amount
    }


# ─────────────────────────────────────────
# ALERT SYSTEM
# ─────────────────────────────────────────

def get_alerts(user_id):
    """
    Generate financial alerts based on spending patterns:
    - Budget deficit alert
    - High spending category alert (>40%)
    - Warning category alert (>30%)
    - Healthy savings alert
    - No income alert
    """
    df = get_transactions_df(user_id)
    alerts = []

    if df.empty:
        return alerts

    income_df = df[df['type'] == 'income']
    expense_df = df[df['type'] == 'expense']

    total_income = income_df['amount'].sum()
    total_expense = expense_df['amount'].sum()
    balance = total_income - total_expense

    # Alert 1 - Budget Deficit
    if total_expense > total_income:
        alerts.append({
            'type': 'danger',
            'icon': '🔴',
            'title': 'Budget Deficit!',
            'message': f'Your expenses (₹{total_expense:,.2f}) exceed your income (₹{total_income:,.2f}) by ₹{abs(balance):,.2f}. Reduce spending immediately!'
        })

    # Alert 2 - No Income recorded
    if total_income == 0 and total_expense > 0:
        alerts.append({
            'type': 'warning',
            'icon': '⚠️',
            'title': 'No Income Recorded',
            'message': 'You have expenses but no income recorded. Add your income sources to get accurate analysis.'
        })

    # Alert 3 - Category overspending
    if not expense_df.empty and total_expense > 0:
        category_group = expense_df.groupby('category')['amount'].sum()
        for category, amount in category_group.items():
            pct = (amount / total_expense) * 100
            if pct > 40:
                alerts.append({
                    'type': 'danger',
                    'icon': '🔴',
                    'title': f'High Spending: {category}',
                    'message': f'{category} accounts for {pct:.1f}% (₹{amount:,.2f}) of your total expenses. Consider reducing this.'
                })
            elif pct > 30:
                alerts.append({
                    'type': 'warning',
                    'icon': '🟡',
                    'title': f'Watch Out: {category}',
                    'message': f'{category} is {pct:.1f}% (₹{amount:,.2f}) of your expenses. Keep an eye on this category.'
                })

    # Alert 4 - Healthy savings
    if total_income > 0:
        savings_rate = (balance / total_income) * 100
        if savings_rate >= 20:
            alerts.append({
                'type': 'success',
                'icon': '🟢',
                'title': 'Healthy Savings!',
                'message': f'Great job! You are saving {savings_rate:.1f}% of your income. Keep it up!'
            })
        elif savings_rate < 10 and savings_rate > 0:
            alerts.append({
                'type': 'warning',
                'icon': '🟡',
                'title': 'Low Savings Rate',
                'message': f'You are only saving {savings_rate:.1f}% of your income. Try to aim for at least 20%.'
            })

    return alerts


# ─────────────────────────────────────────
# BUDGET SUGGESTIONS
# ─────────────────────────────────────────

def get_suggestions(user_id):
    """Generate personalized budget suggestions"""
    df = get_transactions_df(user_id)
    suggestions = []

    if df.empty:
        return suggestions

    income_df = df[df['type'] == 'income']
    expense_df = df[df['type'] == 'expense']

    total_income = income_df['amount'].sum()
    total_expense = expense_df['amount'].sum()

    if total_income == 0:
        return suggestions

    savings_rate = ((total_income - total_expense) / total_income) * 100

    # Suggestion 1 - 50/30/20 Rule
    needs_budget = round(total_income * 0.50, 2)
    wants_budget = round(total_income * 0.30, 2)
    savings_budget = round(total_income * 0.20, 2)
    suggestions.append({
        'icon': '📊',
        'title': '50/30/20 Budget Rule',
        'message': f'Based on your income of ₹{total_income:,.2f}, aim for: Needs ₹{needs_budget:,.2f} (50%), Wants ₹{wants_budget:,.2f} (30%), Savings ₹{savings_budget:,.2f} (20%).'
    })

    # Suggestion 2 - Savings improvement
    if savings_rate < 20:
        target_savings = round(total_income * 0.20, 2)
        current_savings = round(total_income - total_expense, 2)
        gap = round(target_savings - current_savings, 2)
        suggestions.append({
            'icon': '💡',
            'title': 'Increase Your Savings',
            'message': f'To reach a 20% savings rate, you need to save ₹{gap:,.2f} more per month. Try cutting discretionary expenses.'
        })

    # Suggestion 3 - Top category reduction
    if not expense_df.empty:
        category_group = expense_df.groupby('category')['amount'].sum()
        top_cat = category_group.idxmax()
        top_amt = round(category_group.max(), 2)
        top_pct = round((top_amt / total_expense) * 100, 1)
        if top_pct > 30:
            suggested_reduction = round(top_amt * 0.10, 2)
            suggestions.append({
                'icon': '✂️',
                'title': f'Reduce {top_cat} Spending',
                'message': f'{top_cat} is your biggest expense at {top_pct}%. Reducing it by just 10% would save you ₹{suggested_reduction:,.2f}.'
            })

    # Suggestion 4 - Emergency fund
    monthly_expense = round(total_expense / max(len(expense_df['month'].unique()), 1), 2)
    emergency_fund = round(monthly_expense * 6, 2)
    suggestions.append({
        'icon': '🛡️',
        'title': 'Build an Emergency Fund',
        'message': f'Based on your monthly expenses of ₹{monthly_expense:,.2f}, aim to build an emergency fund of ₹{emergency_fund:,.2f} (6 months of expenses).'
    })

    # Suggestion 5 - Consistent tracking
    suggestions.append({
        'icon': '📅',
        'title': 'Track Consistently',
        'message': 'Record every transaction daily for accurate analysis. Even small expenses add up significantly over time.'
    })

    return suggestions