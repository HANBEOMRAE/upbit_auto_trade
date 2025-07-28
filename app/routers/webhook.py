# app/routers/webhook.py

from fastapi import APIRouter, Request
from app.services import buy, sell

router = APIRouter()

@router.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    symbol = data.get("symbol")
    action = data.get("action")

    if not symbol or not action:
        return {"error": "Invalid payload"}

    action = action.upper()

    if action == "BUY":
        result = buy.execute_buy(symbol)
        return {"message": f"Buy executed for {symbol}", "result": result}
    
    elif action == "SELL":
        result = sell.execute_sell_all(symbol)
        return {"message": f"Sell executed for {symbol}", "result": result}
    
    return {"error": "Invalid action"}