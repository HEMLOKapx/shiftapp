import os
from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

# { date: { teacher: [students] } }
data = {}

days = ["月","火","水","木","金","土","日"]

@app.route("/", methods=["GET","POST"])
def index():

    if request.method == "POST":
        form_type = request.form.get("type")
        teacher = request.form.get("teacher")
        student = request.form.get("student")
        date = request.form.get("date")

        if not date:
            return redirect("/")

        if date not in data:
            data[date] = {}

        # ✅ 講師登録（完全分離）
        if form_type == "teacher":
            if teacher and teacher not in data[date]:
                data[date][teacher] = []

        # ✅ 生徒登録（講師指定なし）
        elif form_type == "student":
            if student and len(data[date]) > 0:

                # その日の最初の講師に割り当て
                first_teacher = list(data[date].keys())[0]

                if len(data[date][first_teacher]) < 5:
                    data[date][first_teacher].append(student)

    # ✅ 表作成（曜日＋日付）
    table = {day: [] for day in days}

    for d_str, teachers in data.items():
        try:
            d = datetime.strptime(d_str,"%Y-%m-%d")
            weekday = days[d.weekday()]
        except:
            continue

        for teacher, students in teachers.items():

            table[weekday].append({
                "date": d_str,
                "teacher": teacher,
                "students": students
            })

    return render_template("index.html", table=table)


# ✅ 削除
@app.route("/delete", methods=["POST"])
def delete():
    date = request.form.get("date")
    teacher = request.form.get("teacher")
    student = request.form.get("student")

    if date in data and teacher in data[date]:
        if student in data[date][teacher]:
            data[date][teacher].remove(student)

        # 空なら整理
        if len(data[date][teacher]) == 0:
            del data[date][teacher]

        if len(data[date]) == 0:
            del data[date]

    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
