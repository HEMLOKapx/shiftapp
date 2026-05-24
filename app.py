import os
import sqlite3
from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

DB_NAME = "shift.db"

days = ["月","火","水","木","金","土","日"]

# ✅ 初期化
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        teacher TEXT,
        student TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


@app.route("/", methods=["GET","POST"])
def index():

    if request.method == "POST":
        form_type = request.form.get("type")
        teacher = request.form.get("teacher")
        student = request.form.get("student")
        date = request.form.get("date")

        if date:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()

            # ✅ 講師登録（student = NULL）
            if form_type == "teacher":
                cur.execute(
                    "INSERT INTO shifts (date, teacher, student) VALUES (?, ?, NULL)",
                    (date, teacher)
                )

            # ✅ 生徒登録（自動割当）
            elif form_type == "student":
                # その日の講師を1人取得
                cur.execute(
                    "SELECT teacher FROM shifts WHERE date=? LIMIT 1",
                    (date,)
                )
                row = cur.fetchone()

                if row:
                    target_teacher = row[0]

                    # ✅ 人数チェック
                    cur.execute(
                        "SELECT COUNT(*) FROM shifts WHERE date=? AND teacher=? AND student IS NOT NULL",
                        (date, target_teacher)
                    )
                    count = cur.fetchone()[0]

                    if count < 5:
                        cur.execute(
                            "INSERT INTO shifts (date, teacher, student) VALUES (?, ?, ?)",
                            (date, target_teacher, student)
                        )

            conn.commit()
            conn.close()

        return redirect("/")

    # ✅ 表作成
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT date, teacher, student FROM shifts")
    rows = cur.fetchall()
    conn.close()

    table = {day: [] for day in days}

    temp = {}

    for date, teacher, student in rows:

        d = datetime.strptime(date,"%Y-%m-%d")
        weekday = days[d.weekday()]
        display = f"{d.month}/{d.day}（{weekday}）"

        key = (weekday, date, teacher)

        if key not in temp:
            temp[key] = {
                "date": date,
                "display": display,
                "teacher": teacher,
                "students": []
            }

        if student:
            temp[key]["students"].append(student)

    for (weekday, _, _), record in temp.items():
        table[weekday].append(record)

    return render_template("index.html", table=table)


# ✅ 削除
@app.route("/delete", methods=["POST"])
def delete():
    date = request.form.get("date")
    teacher = request.form.get("teacher")
    student = request.form.get("student")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM shifts WHERE date=? AND teacher=? AND student=?",
        (date, teacher, student)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
