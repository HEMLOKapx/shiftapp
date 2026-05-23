import os
from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

# { date: { teacher: [students] } }
data = {}

days = ["月", "火", "水", "木", "金", "土", "日"]

@app.route("/", methods=["GET", "POST"])
def index():

    # ✅ 追加
    if request.method == "POST":
        teacher = request.form.get("teacher")
        student = request.form.get("student")
        date = request.form.get("date")

        if teacher and student and date:

            if date not in data:
                data[date] = {}

            if teacher not in data[date]:
                data[date][teacher] = []

            # ✅ 最大5人
            if len(data[date][teacher]) < 5:
                data[date][teacher].append(student)

    # ✅ 表作成
    table = {}
    date_map = {}

    for d_str, teachers in data.items():
        try:
            d = datetime.strptime(d_str, "%Y-%m-%d")
            weekday = days[d.weekday()]
        except:
            continue

        for teacher, students in teachers.items():

            if teacher not in table:
                table[teacher] = {day: [] for day in days}
                date_map[teacher] = {}

            # ✅ 重要：上書きせず追加
            table[teacher][weekday].extend(students)

            date_map[teacher][weekday] = d_str

    return render_template("index.html", table=table, date_map=date_map)


# ✅ 削除
@app.route("/delete", methods=["POST"])
def delete():
    date = request.form.get("date")
    teacher = request.form.get("teacher")
    student = request.form.get("student")

    if date in data and teacher in data[date]:

        if student in data[date][teacher]:
            data[date][teacher].remove(student)

        if len(data[date][teacher]) == 0:
            del data[date][teacher]

        if len(data[date]) == 0:
            del data[date]

    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
