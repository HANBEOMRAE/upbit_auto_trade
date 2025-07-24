import os
import pyupbit
from dotenv import load_dotenv
from app.utils.state_manager import load_state, save_state

load_dotenv()
upbit = pyupbit.Upbit(
    os.getenv("UPBIT_ACCESS_KEY"),
    os.getenv("UPBIT_SECRET_KEY")
)

def execute_buy(symbol: str):
    state = load_state()
    capital = state.get(symbol, {}).get("capital", 1_000_000)

    price = pyupbit.get_current_price(symbol)
    if price is None:
        print(f"[오류] {symbol} 현재가 조회 실패")
        return

    if capital < 5000:
        print(f"[매수 불가] {symbol} 자본 {capital}원")
        return

    krw_to_use = capital * 0.9995  # 슬리피지 방지
    resp = upbit.buy_market_order(symbol, krw_to_use)

    if resp and "uuid" in resp:
        print(f"[매수 완료] {symbol} {krw_to_use}원 매수 성공")
        state[symbol]["holding"] = True
        state[symbol]["entry_price"] = price
        save_state(state)
    else:
        print(f"[매수 실패] {symbol} 응답: {resp}")
