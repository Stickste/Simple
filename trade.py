import alpaca_trade_api as tradeapi
from recommend import get_recommended_stocks
import os

api = tradeapi.REST(
    os.getenv("ALPACA_API_KEY"),
    os.getenv("ALPACA_SECRET_KEY"),
    "https://paper-api.alpaca.markets",
    api_version="v2"
)

# 1. Alle Positionen verkaufen
for pos in api.list_positions():
    print(f"Verkaufe {pos.qty} x {pos.symbol}")
    api.submit_order(
        symbol=pos.symbol,
        qty=pos.qty,
        side="sell",
        type="market",
        time_in_force="day"
    )

# 2. Neue Empfehlungen holen
stocks = get_recommended_stocks()

# 3. Je Aktie $100 investieren
for symbol in stocks:
    try:
        price = api.get_latest_trade(symbol).price
        qty = int(100 // price)
        if qty > 0:
            print(f"Kaufe {qty} x {symbol}")
            api.submit_order(
                symbol=symbol,
                qty=qty,
                side="buy",
                type="market",
                time_in_force="day"
            )
    except Exception as e:
        print(f"Fehler bei {symbol}: {e}")
