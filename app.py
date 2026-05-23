import os
from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

# { date: { teacher: [students] } }
data = {}

days = ["月", "火", "水", "木", "金", "土", "日"]

@app.route("/", methods=["GET", "POST"])
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

        # ✅ 講師登録
        if form_type == "teacher":
            if teacher and teacher not in data[date]:
                data[date][teacher] = []

        # ✅ 生徒登録（講師指定なし🔥）
        elif form_type == "student":
            if student and len(data[date]) > 0:

                # ✅ その日の最初の講師を取得
                teacher_list = list(data[date].keys())
                target_teacher = teacher_list[0]

                # ✅ 最大5人制限
                if len(data[date][target_teacher]) < 5:
                    data[date][target_teacher].append(student)

    # ✅ 週表作成
    table = {}

    for d_str, teachers in data.items():
        try:
            d = datetime.strptime(d_str, "%Y-%m-%d")
            weekday = days[d.weekday()]
        except:
            continue

        for teacher, students in teachers.items():

            if teacher not in table:
                table[teacher] = {day: [] for day in days}

            table[teacher][weekday].extend(students)

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

    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
