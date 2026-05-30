import os
import sqlite3
from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta

app = Flask(__name__)

DB_NAME = "shift.db"
DAYS = ["月", "火", "水", "木", "金", "土", "日"]

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # 紐付けが不要なため、同じ構造のままシンプルに扱います
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

@app.route("/", methods=["GET", "POST"])
def index():
    today = datetime.today()

    # ✅ POST（登録処理）
    if request.method == "POST":
        form_type = request.form.get("type")
        name = request.form.get("name")
        date = request.form.get("date")

        if date and name:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()

            if form_type == "teacher":
                # 講師として登録（生徒はNULL）
                cur.execute("INSERT INTO shifts (date, teacher, student) VALUES (?, ?, NULL)", (date, name))
            elif form_type == "student":
                # 生徒として登録（講師はNULL）
                cur.execute("INSERT INTO shifts (date, NULL, ?) VALUES (?, ?, ?)", (date, name))

            conn.commit()
            conn.close()

            # 登録した日付の週へ移動
            d = datetime.strptime(date, "%Y-%m-%d")
            week_offset = (d - today).days // 7
            return redirect(f"/?week={week_offset}")

    # ✅ GET（表示処理）
    offset = request.args.get("week", 0, type=int)
    start = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    
    # 1週間分（7日分）の日付オブジェクトを作成
    week_dates = [start + timedelta(days=i) for i in range(7)]

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # 今週のデータを一括取得
    cur.execute(
        "SELECT date, teacher, student FROM shifts WHERE date BETWEEN ? AND ?",
        (week_dates[0].strftime("%Y-%m-%d"), week_dates[6].strftime("%Y-%m-%d"))
    )
    rows = cur.fetchall()
    conn.close()

    # テンプレートに渡す7日分のデータ構造を初期化
    week_data = []
    for i, d in enumerate(week_dates):
        week_data.append({
            "date_str": d.strftime("%Y-%m-%d"),
            "display_date": f"{d.month}/{d.day}",
            "weekday": DAYS[i],
            "weekday_idx": i,
            "teachers": [],
            "students": []
        })

    # 取得したデータを日付ごとに「講師」「生徒」に振り分け
    for date_str, teacher, student in rows:
        for day in week_data:
            if day["date_str"] == date_str:
                if teacher:
                    day["teachers"].append(teacher)
                if student:
                    day["students"].append(student)

    return render_template(
        "index.html",
        week_data=week_data,
        offset=offset
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
