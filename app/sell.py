import os
import pyupbit
from dotenv import load_dotenv

load_dotenv()
upbit = pyupbit.Upbit(os.getenv("UPBIT_ACCESS_KEY"), os.getenv("UPBIT_SECRET_KEY"))

def execute_sell(symbol: str):
    balance = upbit.get_balances()
    qty = 0
    for item in balance:
        if item['currency'] in symbol:
            qty = float(item['balance'])
            break

    if qty <= 0:
        print(f"[매도] {symbol} 보유량 없음")
        return

    resp = upbit.sell_market_order(symbol, qty)
    print(f"[매도] {symbol} {qty:.4f}개 전량 매도 완료")
    return resp
