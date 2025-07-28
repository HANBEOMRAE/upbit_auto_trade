# app/services/buy.py

from app.clients.upbit_client import get_upbit_client
from app.services.state import set_buy_state, set_tp_order_uuid
import math
import time

def _round_down(value: float, decimals: int = 8) -> float:
    return math.floor(value * (10 ** decimals)) / (10 ** decimals)

def _round_up(value: float, decimals: int = 0) -> float:
    return math.ceil(value * (10 ** decimals)) / (10 ** decimals)

def execute_buy(symbol: str):
    try:
        upbit = get_upbit_client()
        krw = 1_000_000  # 100만원
        if not krw:
            raise Exception("KRW 잔고 조회 실패")

        amount = int(krw * 0.98)
        if amount < 5100:
            raise Exception("주문 금액 부족")

        # ✅ 시장가 매수
        result = upbit.buy_market_order(symbol, amount)
        print(f"[BUY] {symbol} 매수 요청 완료: {result}")

        uuid = result.get("uuid")
        if not uuid:
            raise Exception("UUID가 응답에 없습니다")

        # ✅ 체결 대기 후 주문 정보 조회
        time.sleep(0.5)
        order = upbit.get_order(uuid)
        print(f"[ORDER INFO] {symbol}: {order}")

        # ✅ 체결 수량
        executed_volume = float(order.get("executed_volume", 0))

        # ✅ 체결 가격: trades[0]["price"] 사용
        trades = order.get("trades", [])
        if not trades or float(trades[0]["volume"]) == 0:
            raise Exception("체결 정보 부족: trades 없음 또는 체결 수량 0")

        entry_price = float(trades[0]["price"])  # ← 실제 체결 단가

        if executed_volume <= 0 or entry_price <= 0:
            raise Exception("체결 정보 계산 실패")

        # ✅ 상태 저장
        total_volume = _round_down(executed_volume)
        set_buy_state(symbol, entry_price, total_volume)

        # ✅ 1차 익절 TP 주문 등록
        tp_price = _round_up(entry_price * 1.05, 0)  # 원단위로 반올림
        tp_volume = _round_down(total_volume * 0.5)

        tp_order = upbit.sell_limit_order(symbol, tp_volume, tp_price)
        tp_uuid = tp_order.get("uuid")
        set_tp_order_uuid(symbol, tp_uuid)

        print(f"[TP 예약] {symbol} 지정가 매도 주문 등록: {tp_volume} @ {tp_price}, UUID: {tp_uuid}")
        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[BUY ERROR] {symbol} 매수 실패: {str(e)}")
        return None