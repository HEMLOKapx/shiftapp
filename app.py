import os
from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

# { date: { teacher, students } }
data = {}

days = ["月", "火", "水", "木", "金", "土", "日"]

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        form_type = request.form.get("type")
        date = request.form.get("date")

        if date not in data:
            data[date] = {"teacher": "", "students": []}

        # ✅ 講師登録
        if form_type == "teacher":
            teacher = request.form.get("teacher")
            if teacher:
                data[date]["teacher"] = teacher

        # ✅ 生徒登録
        elif form_type == "student":
            student = request.form.get("student")
            if student and len(data[date]["students"]) < 5:
                data[date]["students"].append(student)

    # ✅ 週表作成
    table = {}

    for d_str, info in data.items():
        try:
            d = datetime.strptime(d_str, "%Y-%m-%d")
            weekday = days[d.weekday()]
        except:
            continue

        teacher = info["teacher"]
        students = info["students"]

        if not teacher:
            continue

        if teacher not in table:
            table[teacher] = {day: [] for day in days}

        # ✅ 表に追加
        table[teacher][weekday] = students

    return render_template("index.html", table=table)


# ✅ 削除
@app.route("/delete", methods=["POST"])
def delete():
    date = request.form.get("date")
    student = request.form.get("student")

    if date in data:
        if student in data[date]["students"]:
            data[date]["students"].remove(student)

    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
