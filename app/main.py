from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

# 앱 루트 확인용
@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Flask server is running"})

# 웹훅 처리 엔드포인트
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    symbol = data.get("symbol")
    action = data.get("action")

    if not symbol or not action:
        return jsonify({"error": "symbol or action missing"}), 400

    script_dir = os.path.join(os.path.dirname(__file__), "app")
    try:
        if action.upper() == "BUY":
            subprocess.Popen(["python3", "buy.py", symbol], cwd=script_dir)
        elif action.upper() == "SELL":
            subprocess.Popen(["python3", "sell.py", symbol], cwd=script_dir)
        else:
            return jsonify({"error": "Invalid action"}), 400

        return jsonify({"status": "success", "symbol": symbol, "action": action})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
