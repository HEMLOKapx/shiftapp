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

            # ✅ 講師登録
            if form_type == "teacher":
                if teacher:
                    cur.execute(
                        "INSERT INTO shifts (date, teacher, student) VALUES (?, ?, NULL)",
                        (date, teacher)
                    )

            # ✅ 生徒登録（講師自動割当）
            elif form_type == "student":
                cur.execute(
                    "SELECT teacher FROM shifts WHERE date=? LIMIT 1",
                    (date,)
                )
                row = cur.fetchone()

                if row:
                    target_teacher = row[0]

                    # ✅ 最大5人制限
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

    # ✅ 週切替
    offset = request.args.get("week", 0, type=int)

    today = datetime.today()
    start = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    end = start + timedelta(days=6)

    week_dates = [start + timedelta(days=i) for i in range(7)]

    # ✅ ヘッダー
    headers = [
        f"{d.month}/{d.day}（{days[i]}）"
        for i, d in enumerate(week_dates)
    ]

    # ✅ DB取得
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT date, teacher, student FROM shifts")
    rows = cur.fetchall()
    conn.close()

    table = {}

    for date, teacher, student in rows:

        if not date or not teacher:
            continue

        d = datetime.strptime(date, "%Y-%m-%d")

        if not (start <= d <= end):
            continue

        weekday = d.weekday()

        if teacher not in table:
            table[teacher] = {i: [] for i in range(7)}

        if student:
            table[teacher][weekday].append(student)

    return render_template(
        "index.html",
        table=table,
        headers=headers,
        offset=offset
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
