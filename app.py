import os
import sqlite3
from flask import Flask, render_template, request
from datetime import datetime, timedelta

app = Flask(__name__)

DB_NAME = "shift.db"
days = ["月","火","水","木","金","土","日"]

@app.route("/")
def index():

    # ✅ 週切替
    offset = request.args.get("week", 0, type=int)

    today = datetime.today()
    start = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    week_dates = [start + timedelta(days=i) for i in range(7)]

    # ✅ ヘッダー（日付＋曜日）
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

    # ✅ テーブル（講師 × 曜日）
    table = {}

    for date, teacher, student in rows:

        d = datetime.strptime(date, "%Y-%m-%d")

        # ✅ 今週だけ
        if not (start <= d <= start + timedelta(days=6)):
            continue

        weekday = d.weekday()

        if teacher not in table:
            table[teacher] = {i: [] for i in range(7)}

        # ✅ 生徒だけ追加
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
