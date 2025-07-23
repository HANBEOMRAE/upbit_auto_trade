import sys, os, pyupbit
from dotenv import load_dotenv
from app.utils.state_manager import load_state, save_state

# 📌 환경변수 로드
load_dotenv()

# 📌 Upbit API 연결
upbit = pyupbit.Upbit(
    os.getenv("UPBIT_ACCESS_KEY"),
    os.getenv("UPBIT_SECRET_KEY")
)

# 📌 심볼 전달받음 (ex: "KRW-XRP")
symbol = sys.argv[1]

# 📌 상태 로드
state = load_state()

# ✅ 보유하지 않으면 매도 금지
if not state[symbol]["holding"]:
    print(f"[보유 없음] {symbol} 보유 중 아님")
    sys.exit()

try:
    # 📌 보유 수량 확인
    balance = upbit.get_balance(symbol)
    if balance is None or balance < 1e-6:
        print(f"[오류] {symbol} 보유 수량 조회 실패 또는 수량 부족")
        sys.exit()

    # 📌 현재가, 진입가 조회
    price = pyupbit.get_current_price(symbol)
    entry = state[symbol]["entry_price"]
    if price is None or entry == 0:
        print(f"[오류] 가격 조회 실패 또는 진입가 0")
        sys.exit()

    # 📌 수익률 계산
    profit_pct = (price - entry) / entry

    # 📌 시장가 전량 매도
    order = upbit.sell_market_order(symbol, balance)

    # ✅ 주문 성공 시 상태 업데이트
    if order:
        state[symbol]["capital"] *= (1 + profit_pct)
        state[symbol]["holding"] = False
        state[symbol]["entry_price"] = 0.0
        save_state(state)
        print(f"[매도 완료] {symbol} 수익률: {profit_pct * 100:.2f}%")
    else:
        print(f"[매도 실패] {symbol} 주문 실패")

except Exception as e:
    print(f"[에러 발생] {symbol} 매도 중 오류: {str(e)}")
    sys.exit()
