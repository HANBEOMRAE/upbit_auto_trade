# app/services/buy.py
import math
import time
import pyupbit  # ✅ 추가
from app.clients.upbit_client import get_upbit_client
from app.services.state import set_buy_state, set_tp_order_uuid

DUST_SKIP_KRW = 1_000  # ✅ 1,000원 이상이면 중복 진입 방지

def _round_down(value: float, decimals: int = 8) -> float:
    return math.floor(value * (10 ** decimals)) / (10 ** decimals)

def _round_up(value: float, decimals: int = 0) -> float:
    return math.ceil(value * (10 ** decimals)) / (10 ** decimals)

def execute_buy(symbol: str):
    try:
        upbit = get_upbit_client()

        # ✅ 현재가, 보유 수량으로 중복 진입 여부 판단
        price = pyupbit.get_current_price(symbol)
        coin = symbol.split("-")[1]
        holding_qty = float(upbit.get_balance(coin) or 0)
        holding_value = (price or 0) * holding_qty

        if holding_value >= DUST_SKIP_KRW:
            msg = {
                "status": "skipped_error",
                "reason": "position_over_threshold",
                "holding_qty": holding_qty,
                "holding_value": int(holding_value)
            }
            print(f"[SKIP] {symbol}: {msg}")
            return msg  # ✅ FastAPI가 그대로 JSON으로 반환하게 됨

        # ✅ (요청대로) 고정 자본 100만원의 98% 사용
        amount = 980_000
        if amount < 5100:
            return {"status": "skipped_error", "reason": "amount_too_small", "amount": amount}

        # ✅ 시장가 매수
        result = upbit.buy_market_order(symbol, amount)
        print(f"[BUY] {symbol} 매수 요청 완료: {result}")

        uuid = result.get("uuid")
        if not uuid:
            return {"status": "failed", "reason": "uuid_missing", "raw": result}

        time.sleep(0.5)
        order = upbit.get_order(uuid)
        print(f"[ORDER INFO] {symbol}: {order}")

        executed_volume = float(order.get("executed_volume", 0))
        trades = order.get("trades", [])
        if not trades or float(trades[0]["volume"]) == 0:
            return {"status": "failed", "reason": "no_trades_or_zero_volume", "order": order}

        entry_price = float(trades[0]["price"])
        if executed_volume <= 0 or entry_price <= 0:
            return {"status": "failed", "reason": "invalid_execution_info", "order": order}

        total_volume = _round_down(executed_volume)
        set_buy_state(symbol, entry_price, total_volume)

        tp_price = _round_up(entry_price * 1.05, 0)
        tp_volume = _round_down(total_volume * 0.5)

        tp_order = upbit.sell_limit_order(symbol, tp_volume, tp_price)
        tp_uuid = tp_order.get("uuid")
        set_tp_order_uuid(symbol, tp_uuid)

        print(f"[TP 예약] {symbol} 지정가 매도 주문 등록: {tp_volume} @ {tp_price}, UUID: {tp_uuid}")
        return {
            "status": "ok",
            "entry_price": entry_price,
            "total_volume": total_volume,
            "tp_price": tp_price,
            "tp_volume": tp_volume,
            "tp_uuid": tp_uuid
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[BUY ERROR] {symbol} 매수 실패: {str(e)}")
        return {"status": "error", "error": str(e)}