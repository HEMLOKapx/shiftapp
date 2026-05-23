import os
from flask import Flask, render_template, request

app = Flask(__name__)

data = {}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("date")

        if date not in data:
            data[date] = []

        data[date].append(name)

    return render_template("index.html", data=data)

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
``

