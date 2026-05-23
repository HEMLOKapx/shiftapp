import os
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# データ保存（簡易：メモリ）
data = {}

# ✅ トップページ（表示＋追加）
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("date")

        if date and name:
            if date not in data:
                data[date] = []

            data[date].append(name)

    return render_template("index.html", data=data)

# ✅ 削除処理
@app.route("/delete", methods=["POST"])
def delete():
    date = request.form.get("date")
    name = request.form.get("name")

    if date in data:
        if name in data[date]:
            data[

        # 空になったら日付ごと削除
        if len(data[date]) == 0:
            del data[date]

    return redirect("/")

# ✅ Render対応
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
