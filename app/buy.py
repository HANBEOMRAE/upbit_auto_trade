import os
import pyupbit
from dotenv import load_dotenv

load_dotenv()
upbit = pyupbit.Upbit(os.getenv("UPBIT_ACCESS_KEY"), os.getenv("UPBIT_SECRET_KEY"))

INITIAL_KRW = 1_000_000  # 초기 자본

def execute_buy(symbol: str):
    price = pyupbit.get_current_price(symbol)
    if price is None:
        print(f"[에러] 현재가 조회 실패: {symbol}")
        return

    volume = INITIAL_KRW / price
    resp = upbit.buy_market_order(symbol, volume)
    print(f"[매수] {symbol} {volume:.4f}개 매수 주문 완료")
    return resp
