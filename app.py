from flask import Flask
from database.db_connection import init_db

app = Flask(__name__)
app.secret_key = "pfms_secret_key"

# Initialize database on startup
init_db()

@app.route('/')
def home():
    return "PFMS is running!"

if __name__ == '__main__':
    app.run(debug=True)