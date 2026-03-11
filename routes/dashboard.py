from flask import Blueprint, render_template, session, redirect, url_for
from routes.auth import login_required

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
@login_required
def index():
    return render_template('dashboard.html', username=session['username'])