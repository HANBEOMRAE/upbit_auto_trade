from fastapi import FastAPI
from pydantic import BaseModel
from app.utils.state_manager import load_state, save_state
from app.buy import execute_buy
from app.sell import execute_sell

app = FastAPI()
state = load_state()

# ✅ 루트 확인용 엔드포인트
@app.get("/")
async def root():
    return {"message": "Upbit Auto Trade Server is running"}

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
            "entry_price": 0.0
        }

    # ... 이후 매수/매도 로직
