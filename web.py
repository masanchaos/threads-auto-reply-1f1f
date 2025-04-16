from flask import Flask
import main
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Threads 留言機器人已啟動"

@app.route("/run")
def run_bot():
    main.auto_comment()
    return "✅ 自動留言執行完成！"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
