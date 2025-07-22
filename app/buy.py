import sys, os, pyupbit
from dotenv import load_dotenv
from app.utils.state_manager import load_state, save_state

# .env에서 환경 변수 불러오기
load_dotenv()

# Upbit API 연결
upbit = pyupbit.Upbit(
    os.getenv("UPBIT_ACCESS_KEY"),
    os.getenv("UPBIT_SECRET_KEY")
)

# 웹훅으로부터 전달받은 심볼
symbol = sys.argv[1]

# 현재 상태 불러오기
state = load_state()

# 이미 보유 중이면 매수 안함
if state[symbol]["holding"]:
    print(f"{symbol} 이미 보유 중")
    sys.exit()

# 현재가 조회
price = pyupbit.get_current_price(symbol)

# 현재 자본 확인
krw_amount = state[symbol]["capital"]

# 최소 주문 금액 확인 (업비트 기준 약 5,000원)
if krw_amount < 5000:
    print("최소 주문 금액 부족")
    sys.exit()

# 시장가 매수 실행 (수수료 고려 99.95%)
order = upbit.buy_market_order(symbol, krw_amount * 0.9995)

# 주문 성공 시 상태 업데이트
if order:
    state[symbol]["holding"] = True
    state[symbol]["entry_price"] = price
    save_state(state)
    print(f"{symbol} 매수 완료: 진입가 {price}")
