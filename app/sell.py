import os
import pyupbit
from dotenv import load_dotenv
from app.utils.state_manager import load_state, save_state

load_dotenv()
upbit = pyupbit.Upbit(
    os.getenv("UPBIT_ACCESS_KEY"),
    os.getenv("UPBIT_SECRET_KEY")
)

def execute_sell(symbol: str):
    state = load_state()
    coin = symbol.split("-")[1]

    balances = upbit.get_balances()
    qty = 0
    for item in balances:
        if item['currency'] == coin:
            qty = float(item['balance'])
            break

    if qty <= 0:
        print(f"[매도 실패] {symbol} 보유량 없음")
        return

    price = pyupbit.get_current_price(symbol)
    entry_price = state[symbol].get("entry_price", 0)

    if price is None or entry_price == 0:
        print(f"[에러] {symbol} 현재가 또는 진입가 오류")
        return

    profit_rate = (price - entry_price) / entry_price
    resp = upbit.sell_market_order(symbol, qty)

    if resp and "uuid" in resp:
        capital = state[symbol].get("capital", 1_000_000)
        capital *= (1 + profit_rate)
        state[symbol]["capital"] = capital
        state[symbol]["holding"] = False
        state[symbol]["entry_price"] = 0.0
        save_state(state)
        print(f"[매도 완료] {symbol} 수익률: {profit_rate * 100:.2f}%, 자본 갱신: {capital:.2f}원")
    else:
        print(f"[매도 실패] {symbol} 응답: {resp}")
