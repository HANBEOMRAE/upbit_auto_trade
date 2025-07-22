import sys, os, pyupbit
from dotenv import load_dotenv
from app.utils.state_manager import load_state, save_state

# .env 로드
load_dotenv()

# Upbit API 연결
upbit = pyupbit.Upbit(
    os.getenv("UPBIT_ACCESS_KEY"),
    os.getenv("UPBIT_SECRET_KEY")
)

# 심볼 파라미터
symbol = sys.argv[1]

# 상태 파일 로드
state = load_state()

# 보유 상태 아니면 매도 불가
if not state[symbol]["holding"]:
    print(f"{symbol} 보유 없음")
    sys.exit()

# 보유 수량 조회
balance = upbit.get_balance(symbol)

# 현재가 및 진입가
price = pyupbit.get_current_price(symbol)
entry = state[symbol]["entry_price"]

# 수익률 계산
profit_pct = (price - entry) / entry

# 시장가 전량 매도
order = upbit.sell_market_order(symbol, balance)

# 자본 갱신 (복리 방식)
state[symbol]["capital"] *= (1 + profit_pct)
state[symbol]["holding"] = False
state[symbol]["entry_price"] = 0.0

# 상태 저장
save_state(state)

print(f"{symbol} 매도 완료. 수익률: {profit_pct * 100:.2f}%")
