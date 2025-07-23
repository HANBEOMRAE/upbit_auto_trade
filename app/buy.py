import sys, os, pyupbit
from dotenv import load_dotenv
from app.utils.state_manager import load_state, save_state

# 📌 환경 변수 로드
load_dotenv()

# 📌 업비트 API 객체 생성
upbit = pyupbit.Upbit(
    os.getenv("UPBIT_ACCESS_KEY"),
    os.getenv("UPBIT_SECRET_KEY")
)

# 📌 웹훅으로부터 전달받은 종목 심볼 (예: "KRW-XRP")
symbol = sys.argv[1]

# 📌 현재 상태 로드
state = load_state()

# ✅ 중복 진입 방지
if state[symbol]["holding"]:
    print(f"[중복방지] {symbol} 이미 보유 중입니다.")
    sys.exit()

try:
    # 📌 현재가 조회
    price = pyupbit.get_current_price(symbol)
    if price is None:
        print(f"[오류] {symbol} 현재가 조회 실패")
        sys.exit()

    # 📌 보유 자본 확인
    krw_amount = state[symbol]["capital"]

    # ✅ 최소 주문 금액 조건 (업비트 최소: 5,000원)
    if krw_amount < 5000:
        print(f"[자본 부족] {symbol} 자본 {krw_amount}원으로 매수 불가")
        sys.exit()

    # 📌 시장가 매수 실행 (수수료 고려)
    order = upbit.buy_market_order(symbol, krw_amount * 0.9995)

    # ✅ 주문 성공 시 상태 업데이트
    if order and "uuid" in order:
        state[symbol]["holding"] = True
        state[symbol]["entry_price"] = price
        save_state(state)
        print(f"[매수 성공] {symbol} 진입가 {price}원")
    else:
        print(f"[매수 실패] {symbol} 주문 실패 응답: {order}")

except Exception as e:
    print(f"[에러] {symbol} 매수 중 예외 발생: {str(e)}")
    sys.exit()
