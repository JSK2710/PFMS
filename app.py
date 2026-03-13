from flask import Flask, redirect, url_for
from database.db_connection import init_db
from routes.auth import auth
from routes.dashboard import dashboard
from routes.transactions import transactions


app = Flask(__name__)
app.secret_key = "pfms_secret_key"

# Initialize database on startup
init_db()


# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(transactions)

# Redirect root to login
@app.route('/')
def home():
    return "PFMS is running!"

if __name__ == '__main__':
    app.run(debug=True)