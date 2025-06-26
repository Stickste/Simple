import os
import time
from alpaca import api as alpaca_api
import alpaca_trade_api as tradeapi

# Only load .env if not running in CI (GitHub Actions)
if not os.getenv("GITHUB_ACTIONS"):
    from dotenv import load_dotenv
    load_dotenv()


MAX_BUYS = 3

alp_key = os.getenv("ALPACA_API_KEY")
alp_secret = os.getenv("ALPACA_SECRET_KEY")

api = tradeapi.REST(alp_key, alp_secret, "https://paper-api.alpaca.markets")

def buy_stocks(tickers):
    """Liquidiert alte Positionen & kauft neue gleichgewichtet."""
    try:
        # ── Offene Positionen schließen
        positions = alpaca_api.list_positions()
        if positions:
            print("🧹 Verkaufe bestehende Positionen...")
            for position in positions:
                try:
                    alpaca_api.submit_order(
                        symbol       = position.symbol,
                        qty          = position.qty,
                        side         = "sell",
                        type         = "market",
                        time_in_force= "day"
                    )
                    print(f"✅ Verkauf: {position.symbol} ({position.qty} Stk)")
                except Exception as e:
                    print(f"⚠️ Fehler beim Verkauf von {position.symbol}: {e}")
            time.sleep(2)

        account = alpaca_api.get_account()
        cash = float(account.cash)
        print(f"💵 Verfügbares Kapital: {cash:,.2f} USD")

        allocation = cash / MAX_BUYS
        print(f"📊 Kapital pro Aktie:  {allocation:,.2f} USD")

        

        # ── Neue Käufe
        for ticker in tickers:
            try:
                last_trade = alpaca_api.get_latest_trade(ticker)
                last_price = float(last_trade.price)
                qty = int(allocation / last_price)
                if qty < 1:
                    print(f"⚠️ {ticker}: Preis zu hoch für {allocation:,.2f} USD.")
                    continue

                alpaca_api.submit_order(
                    symbol       = ticker,
                    qty          = qty,
                    side         = "buy",
                    type         = "market",
                    time_in_force= "day"
                )
                print(f"✅ Kauf: {ticker} ({qty} Stk, ~{qty * last_price:,.2f} USD)")
            except Exception as e:
                print(f"❌ Fehler beim Kauf von {ticker}: {e}")

    except Exception as e:
        print(f"❌ Fehler beim Abrufen von Kontodaten: {e}")