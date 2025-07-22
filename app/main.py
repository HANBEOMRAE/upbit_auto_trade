from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "Flask server is running"})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    symbol = data.get("symbol")
    action = data.get("action")

    if not symbol or not action:
        return jsonify({"error": "symbol or action missing"}), 400

    if action.upper() == "BUY":
        subprocess.Popen(["python3", "app/buy.py", symbol])
    elif action.upper() == "SELL":
        subprocess.Popen(["python3", "app/sell.py", symbol])
    else:
        return jsonify({"error": "Invalid action"}), 400

    return jsonify({"status": "success", "symbol": symbol, "action": action})
