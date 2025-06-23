import os
import json
import random
from alpaca import api as alpaca_api
from time import sleep
from yfin import get_technical_summary
from news import get_news_articles
from recommend import should_buy_stock
# from alpaca import buy_stocks  # uncomment to enable real buying
from sp500 import fetch_sp500_tickers

MAX_BUYS = 3
FILENAME = "technical_summary.json"

def buy_stocks(tickers):
    try:
        account = alpaca_api.get_account()
        print(f"💵 Verfügbares Kapital: {float(account.cash):.2f} USD")

        # Bestehende Positionen verkaufen
        positions = alpaca_api.list_positions()
        if positions:
            print("🧹 Verkaufe bestehende Positionen...")
            for position in positions:
                try:
                    alpaca_api.submit_order(
                        symbol=position.symbol,
                        qty=position.qty,
                        side="sell",
                        type="market",
                        time_in_force="day"
                    )
                    print(f"✅ Verkauf: {position.symbol} ({position.qty} Stück)")
                except Exception as e:
                    print(f"⚠️ Fehler beim Verkauf von {position.symbol}: {e}")

        # Neue Käufe (1000 USD pro Ticker)
        for ticker in tickers:
            try:
                last_trade = alpaca_api.get_latest_trade(ticker)
                last_price = float(last_trade.price)
                qty = int(1000 / last_price)
                if qty < 1:
                    print(f"⚠️ {ticker}: Preis zu hoch für 1000 USD Investition.")
                    continue

                alpaca_api.submit_order(
                    symbol=ticker,
                    qty=qty,
                    side="buy",
                    type="market",
                    time_in_force="day"
                )
                print(f"✅ Kauf: {ticker} ({qty} Stück, ~{qty * last_price:.2f} USD)")
            except Exception as e:
                print(f"❌ Fehler beim Kauf von {ticker}: {e}")

    except Exception as e:
        print(f"❌ Fehler beim Abrufen von Kontodaten: {e}")

def classify_bullish_signal(tech_data: dict) -> str:
    try:
        dates = list(tech_data.keys())
        if len(dates) < 2:
            return "none"

        last_day = dates[-1]
        prev_day = dates[-2]
        today = tech_data[last_day]
        yesterday = tech_data[prev_day]

        # Kernkriterien
        macd_bullish = today["macd_bullish"] and today["MACD_hist"] > 0
        rsi_ok = today["RSI14"] < 70
        sma_ok = today["SMA14"] > today["SMA50"]
        price_ok = today["Close"] > today["SMA14"]
        obv_rising = today["OBV"] > yesterday["OBV"]

        # Starke Empfehlung: Alle erfüllt
        if macd_bullish and rsi_ok and sma_ok and price_ok and obv_rising:
            return "strong"

        # Moderate Empfehlung: MACD & RSI stimmen, aber z. B. SMA oder OBV nicht ideal
        elif macd_bullish and rsi_ok and (sma_ok or price_ok):
            return "moderate"

        # Schwache Empfehlung: Nur MACD bullish
        elif macd_bullish:
            return "weak"

        else:
            return "none"

    except Exception as e:
        print(f"⚠️ Fehler bei der Einstufung: {e}")
        return "none"


    except Exception as e:
        print(f"⚠️  Fehler beim Prüfen auf Bullish-Signal: {e}")
        return False

def main():
    tickers_to_check = fetch_sp500_tickers()
    random.shuffle(tickers_to_check)  # Random order

    if os.path.exists(FILENAME):
        os.remove(FILENAME)
    chosen_stocks = []
    technical_data = {}


    for ticker in tickers_to_check:
        if len(chosen_stocks) >= MAX_BUYS:
            break
        if '.' in ticker:
            continue  # skip tickers with dot (e.g., BRK.B)
        filename = get_technical_summary(ticker)
        #sleep(0.1)  # avoid rate limits

    # Load the combined technical data
    if not os.path.exists(FILENAME):
        print("❌ Technische Daten wurden nicht gefunden.")
        return

    with open(FILENAME, "r") as f:
        technical_data = json.load(f)

    for ticker in tickers_to_check:
        if len(chosen_stocks) >= MAX_BUYS:
            break
        if ticker not in technical_data:
            continue
        if not classify_bullish_signal(technical_data[ticker]):
            continue

        # Get news + create prompt
        try:
            news = get_news_articles(ticker)
            prompt = f"Based on the following technicals and news, should we buy {ticker} for a day, to sell the next?\n\n" \
                     f"Technicals: {json.dumps(technical_data[ticker])}\n\nNews: {news}"

            print(f"📨 Sende Anfrage an GPT für {ticker}...")
            if should_buy_stock(prompt):
                chosen_stocks.append(ticker)
                print(f"✅ Kaufempfehlung für {ticker}")
            else:
                print(f"⛔️ Keine Empfehlung für {ticker}")
        except Exception as e:
            print(f"❌ Fehler bei {ticker}: {e}")

    if chosen_stocks:
        print(f"\n📈 Empfohlene Aktien: {chosen_stocks}")
        buy_stocks(chosen_stocks)  # Uncomment to enable actual buying
    else:
        print("\n❌ Keine geeigneten Aktien gefunden.")

if __name__ == "__main__":
    main()
