from flask import Flask
import main
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Threads 留言機器人已啟動"

@app.route("/run")
def run_bot():
    try:
        total, commented = main.auto_comment()
        return f"✅ 共掃描 {total} 篇，成功留言 {commented} 篇"
    except Exception as e:
        import traceback
        return f"❌ 發生錯誤：<pre>{traceback.format_exc()}</pre>"




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
