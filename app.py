from flask import Flask

app = Flask(__name__)
app.secret_key = "pfms_secret_key"

@app.route('/')
def home():
    return "PFMS is running!"

if __name__ == '__main__':
    app.run(debug=True)