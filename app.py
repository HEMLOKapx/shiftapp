import os
import sqlite3
from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta

app = Flask(__name__)

DB_NAME = "shift.db"
days = ["月","火","水","木","金","土","日"]

# ✅ DB初期化
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

    # ✅ 登録処理
    if request.method == "POST":
        form_type = request.form.get("type")
        teacher = request.form.get("teacher")
        student = request.form.get("student")
        date = request.form.get("date")

        if date:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()

            if form_type == "teacher":
                cur.execute(
                    "INSERT INTO shifts (date, teacher, student) VALUES (?, ?, NULL)",
                    (date, teacher)
                )

            elif form_type == "student":
                cur.execute("SELECT teacher FROM shifts WHERE date=? LIMIT 1",(date,))
                row = cur.fetchone()

                if row:
                    target_teacher = row[0]

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

    # ✅ 週取得（今日基準）
    today = datetime.today()

    # 👉 月曜開始
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # ✅ DB取得
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT date, teacher, student FROM shifts")
    rows = cur.fetchall()

    conn.close()

    # ✅ テーブル
    table = {i: [] for i in range(7)}
    headers = {}

    temp = {}

    for date, teacher, student in rows:
        d = datetime.strptime(date,"%Y-%m-%d")

        # ✅ 今週だけ表示
        if not (start_of_week <= d <= end_of_week):
            continue

        weekday_index = d.weekday()

        # ✅ ヘッダー（日付＋曜日）
        headers[weekday_index] = f"{d.month}/{d.day}（{days[weekday_index]}）"

        key = (weekday_index, date, teacher)

        if key not in temp:
            temp[key] = {
                "date": date,
                "teacher": teacher,
                "students": []
            }

        if student:
            temp[key]["students"].append(student)

    for (weekday_index, _, _), record in temp.items():
        table[weekday_index].append(record)

    return render_template("index.html", table=table, headers=headers)
