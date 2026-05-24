import os
import sqlite3
from flask import Flask, render_template, request
from datetime import datetime, timedelta

app = Flask(__name__)

DB_NAME = "shift.db"
days = ["月","火","水","木","金","土","日"]

# ✅ DB初期化（これ必須）
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


@app.route("/")
def index():

    offset = request.args.get("week", 0, type=int)

    today = datetime.today()
    start = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    end = start + timedelta(days=6)

    week_dates = [start + timedelta(days=i) for i in range(7)]

    headers = [
        f"{d.month}/{d.day}（{days[i]}）"
        for i, d in enumerate(week_dates)
    ]

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # ✅ studentがNULLでもOKにする
    cur.execute("SELECT date, teacher, student FROM shifts")
    rows = cur.fetchall()

    conn.close()

    table = {}

    for date, teacher, student in rows:

        # ❗ None対策
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
