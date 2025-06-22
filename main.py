import os
import json
import random
from time import sleep
from yfin import get_technical_summary
from news import get_news_articles
from recommend import should_buy_stock
# from alpaca import buy_stocks  # uncomment to enable real buying
from sp500 import fetch_sp500_tickers

MAX_BUYS = 3
FILENAME = "technical_summary.json"

def is_macd_bullish(tech_data: dict) -> bool:
    try:
        last_day = list(tech_data.keys())[-1]
        return tech_data[last_day]["macd_bullish"]
    except Exception as e:
        print(f"⚠️  Fehler beim Prüfen auf MACD bullish: {e}")
        return False

def main():
    tickers_to_check = fetch_sp500_tickers()
    random.shuffle(tickers_to_check)  # Random order

    chosen_stocks = []
    technical_data = {}

    for ticker in tickers_to_check:
        if len(chosen_stocks) >= MAX_BUYS:
            break
        if '.' in ticker:
            continue  # skip tickers with dot (e.g., BRK.B)

        print(f"\n🔎 Prüfe {ticker}...")
        filename = get_technical_summary(ticker)
        sleep(0.5)  # avoid rate limits

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
        if not is_macd_bullish(technical_data[ticker]):
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
        # buy_stocks(chosen_stocks)  # Uncomment to enable actual buying
    else:
        print("\n❌ Keine geeigneten Aktien gefunden.")

if __name__ == "__main__":
    main()
