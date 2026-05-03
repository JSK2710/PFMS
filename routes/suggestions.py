from flask import Blueprint, render_template, session
from routes.auth import login_required
from models.analysis import get_spending_analysis, get_alerts, get_suggestions

suggestions_bp = Blueprint('suggestions', __name__)


@suggestions_bp.route('/suggestions')
@login_required
def suggestions():
    user_id = session['user_id']

    analysis = get_spending_analysis(user_id)
    alerts = get_alerts(user_id)
    budget_suggestions = get_suggestions(user_id)

    return render_template('suggestions.html',
                           analysis=analysis,
                           alerts=alerts,
                           suggestions=budget_suggestions)