from fastapi import FastAPI
from pydantic import BaseModel
from app.utils.state_manager import load_state, save_state
from app.buy import execute_buy
from app.sell import execute_sell

app = FastAPI()
state = load_state()

class TradeSignal(BaseModel):
    symbol: str
    action: str  # "BUY" or "SELL"

@app.post("/webhook")
async def webhook(signal: TradeSignal):
    symbol = signal.symbol.upper()
    action = signal.action.upper()

    if symbol not in state:
        state[symbol] = {
            "holding": False,
            "entry_price": 0.0,
            "capital": 1_000_000
        }

    if action == "BUY":
        if state[symbol]["holding"]:
            return {"status": "Already holding"}
        execute_buy(symbol)

    elif action == "SELL":
        if not state[symbol]["holding"]:
            return {"status": "No position to sell"}
        execute_sell(symbol)

    else:
        return {"error": "Invalid action"}

    save_state(state)
    return {"status": f"{action} executed for {symbol}"}
