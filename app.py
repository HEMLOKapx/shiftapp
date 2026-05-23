import os
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

data = {}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("date")

        if date:
            if date not in data:
                data[date] = []

            data[date].append(name)

    return render_template("index.html", data=data)

@app.route("/delete", methods=["POST"])
def delete():
    date = request.form.get("date")
    name = request.form.get("name")

    if date in data and name in datadata[date].remove(name)

        if len(data[date]) == 0:
            del data[date]

    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
