from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "OK"

print("FLASK TEST STARTING")

app.run(
    host="127.0.0.1",
    port=5000,
    debug=False,
    use_reloader=False
)