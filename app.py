import os
from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

# データ保存（簡易）
data = {}

# 曜日リスト
days = ["月", "火", "水", "木", "金", "土", "日"]

# ✅ メインページ（追加＋表示）
@app.route("/", methods=["GET", "POST"])
def index():

    # ✅ 追加処理
    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("date")

        if name and date:
            if date not in data:
                data[date] = []
            data[date].append(name)

    # ✅ 週表示テーブル作成
    table = {}

    for date, names in data.items():
        try:
            d = datetime.strptime(date, "%Y-%m-%d")
            weekday = days[d.weekday()]  # 曜日に変換
        except:
            continue

        for n in names:
            if n not in table:
                table[n] = {day: "" for day in days}

            table[n][weekday] = "○"

    return render_template("index.html", table=table)

# ✅ 削除処理
@app.route("/delete", methods=["POST"])
def delete():
    date = request.form.get("date")
    name = request.form.get("name")

    if date in data:
        if name in data[date]:
            data[date].remove(name)

        # 空なら日付ごと削除
        if len(data[date]) == 0:
            del data[date]

    return redirect("/")

# ✅ Render対応（必須）
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
