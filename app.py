import os
import sqlite3
from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta

app = Flask(__name__)

DB_NAME = "shift.db"
DAYS = ["月", "火", "水", "木", "金", "土", "日"]
# 指定された4つの時間帯を定義
TIME_SLOTS = ["17:00-17:50", "18:00-18:50", "19:00-19:50", "20:00-20:50"]

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        teacher TEXT,
        student TEXT,
        time_slot TEXT
    )
    """)
    # 既存の古いデータベースがある場合、time_slotカラムを自動で追加する対策
    try:
        cur.execute("ALTER TABLE shifts ADD COLUMN time_slot TEXT")
    except sqlite3.OperationalError:
        pass  # 既にカラムが存在する場合は何もしない
        
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
        time_slot = request.form.get("time_slot")

        if date and name and time_slot:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()

            if form_type == "teacher":
                cur.execute(
                    "INSERT INTO shifts (date, teacher, student, time_slot) VALUES (?, ?, NULL, ?)", 
                    (date, name, time_slot)
                )
            elif form_type == "student":
                cur.execute(
                    "INSERT INTO shifts (date, NULL, ?, time_slot) VALUES (?, ?, ?)", 
                    (date, name, time_slot)
                )

            conn.commit()
            conn.close()

            # 登録した日付の週へ移動
            d = datetime.strptime(date, "%Y-%m-%d")
            week_offset = (d - today).days // 7
            return redirect(f"/?week={week_offset}")

    # ✅ GET（表示処理）
    offset = request.args.get("week", 0, type=int)
    start = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    week_dates = [start + timedelta(days=i) for i in range(7)]

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT date, teacher, student, time_slot FROM shifts WHERE date BETWEEN ? AND ?",
        (week_dates[0].strftime("%Y-%m-%d"), week_dates[6].strftime("%Y-%m-%d"))
    )
    rows = cur.fetchall()
    conn.close()

    # 7日分 × 4時間帯 のデータ構造を初期化
    week_data = []
    for i, d in enumerate(week_dates):
        day_info = {
            "date_str": d.strftime("%Y-%m-%d"),
            "display_date": f"{d.month}/{d.day}",
            "weekday": DAYS[i],
            "weekday_idx": i,
            # 時間帯ごとに先生と生徒のリストを用意
            "slots": {slot: {"teachers": [], "students": []} for slot in TIME_SLOTS}
        }
        week_data.append(day_info)

    # 取得したデータを適切な日付・時間帯に振り分け
    for date_str, teacher, student, time_slot in rows:
        # 時間帯が空の古いデータは一番最初の時間帯に割り当て
        if not time_slot:
            time_slot = TIME_SLOTS[0]
            
        for day in week_data:
            if day["date_str"] == date_str:
                if time_slot in day["slots"]:
                    if teacher:
                        day["slots"][time_slot]["teachers"].append(teacher)
                    if student:
                        day["slots"][time_slot]["students"].append(student)

    return render_template(
        "index.html",
        week_data=week_data,
        offset=offset,
        time_slots=TIME_SLOTS
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
