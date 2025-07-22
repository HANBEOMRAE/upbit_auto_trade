from flask import Flask, request, jsonify
import subprocess

# Flask 앱 생성
app = Flask(__name__)

# 웹훅 엔드포인트 설정
@app.route('/webhook', methods=['POST'])
def webhook():
    # JSON 데이터 수신
    data = request.json
    symbol = data.get("symbol")
    action = data.get("action")

    # 필수값 누락 검사
    if not symbol or not action:
        return jsonify({"error": "symbol or action missing"}), 400

    # BUY 신호 수신 시 buy.py 실행
    if action.upper() == "BUY":
        subprocess.Popen(["python3", "app/buy.py", symbol])
    # SELL 신호 수신 시 sell.py 실행
    elif action.upper() == "SELL":
        subprocess.Popen(["python3", "app/sell.py", symbol])
    else:
        return jsonify({"error": "Invalid action"}), 400

    # 성공 응답
    return jsonify({"status": "success", "symbol": symbol, "action": action})

# 앱 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
