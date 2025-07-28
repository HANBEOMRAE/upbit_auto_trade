# app/services/sell.py

from app.clients.upbit_client import get_upbit_client
from app.services.state import (
    get_total_volume,
    get_tp_order_uuid,
    get_tp_executed_volume,
    set_tp_executed_volume
)
import math
import time

def _round_down(value: float, decimals: int = 8) -> float:
    return math.floor(value * (10 ** decimals)) / (10 ** decimals)

def execute_sell_all(symbol: str):
    try:
        upbit = get_upbit_client()

        total_volume = get_total_volume(symbol)
        uuid = get_tp_order_uuid(symbol)
        tp_volume = 0.0

        # ✅ TP 주문 체결량 조회
        if uuid:
            time.sleep(0.5)
            order = upbit.get_order(uuid)
            print(f"[TP 주문 조회] {symbol} UUID: {uuid} → {order}")

            trades = order.get("trades", [])
            if trades:
                executed_volume = float(order.get("executed_volume", 0))
                tp_volume = _round_down(executed_volume)
                set_tp_executed_volume(symbol, tp_volume)
            else:
                print(f"[TP 미체결] {symbol} 지정가 주문 체결 내역 없음")

        # ✅ 남은 수량 계산
        remaining_volume = _round_down(total_volume - tp_volume)
        if remaining_volume <= 0:
            print(f"[SELL] {symbol} 남은 수량 없음 (총: {total_volume}, TP 체결: {tp_volume})")
            return None

        # ✅ 남은 수량 시장가 매도
        result = upbit.sell_market_order(symbol, remaining_volume)
        print(f"[SELL] {symbol} 시장가로 전량 청산: {remaining_volume}")
        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[SELL ERROR] {symbol} 전량 매도 실패: {str(e)}")
        return None