import alpaca_trade_api as tradeapi
import time
from datetime import datetime, timedelta
from keys import alp_key, alp_endpoint, alp_secret

api = tradeapi.REST(alp_key, alp_secret, alp_endpoint)

empfohlene_aktien = ["TSLA", "MU", "MELI"]
investition_pro_aktie = 100  # USD

for symbol in empfohlene_aktien:
    try:
        quote = api.get_last_trade(symbol)
        preis = quote.price
        menge = int(investition_pro_aktie // preis)

        if menge > 0:
            print(f"Kaufe {menge} Aktien von {symbol} zum Preis von {preis} USD")
            api.submit_order(
                symbol=symbol,
                qty=menge,
                side="buy",
                type="market",
                time_in_force="gtc"
            )
        else:
            print(f"Nicht genug Kapital für {symbol}, Preis zu hoch.")
    except Exception as e:
        print(f"Fehler beim Kaufen von {symbol}: {e}")