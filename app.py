from flask import Flask

app = Flask(__name__)
app.secret_key = "dev-secret-key"

@app.route("/")
def index():
    return "Smart Event Backend Running ✅"

if __name__ == "__main__":
    print("Flask server starting...")
    app.run(debug=True)