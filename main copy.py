import json
import sys
import random
sys.path.append(".")

from yfin import get_technical_summary
from news import get_news_articles
from recommend import client
from alpaca import api as alpaca_api
from sp500 import fetch_sp500_tickers

tickers_to_check = fetch_sp500_tickers()
random.shuffle(tickers_to_check)
chosen_stocks = []
macd_candidates = []

def is_promising_technical(ticker):
    filename = get_technical_summary(ticker)
    with open(filename, "r") as f:
        data = json.load(f)

    last_day = list(data.keys())[-1]
    tech = data[last_day]

    # MACD bullish + RSI unter 70
    return tech.get("macd_bullish", False) and tech.get("RSI14", 100) < 70

def ask_gpt_to_buy(ticker, technical_path, news_data):
    with open(technical_path, "r") as f:
        tech = f.read()

    news_json = json.dumps(news_data, indent=2)
    prompt = (
        f"Hier sind technische Daten für {ticker}:\n{tech}\n\n"
        f"Hier sind relevante Nachrichten:\n{news_json}\n\n"
        "Sollte ich diese Aktie am Montag kaufen und Dienstag verkaufen? "
        "Gib nur 'JA' oder 'NEIN' zurück."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Du bist ein professioneller Aktienhändler."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=5
        )
        answer = response.choices[0].message.content.strip().upper()
        return answer.startswith("JA")
    except Exception as e:
        print(f"GPT Fehler bei {ticker}: {e}")
        return False

# Hauptlogik
if __name__ == "__main__":
    for ticker in tickers_to_check:
        print(f"\n🔎 Prüfe {ticker}...")
        try:
            if is_promising_technical(ticker):
                macd_candidates.append(ticker)
        except Exception as e:
            print(f"⚠️ Fehler bei {ticker}: {e}")

        if len(macd_candidates) >= 10:
            break  # Maximal 10 für GPT

    for ticker in macd_candidates:
        try:
            news = get_news_articles(ticker)
            tech_file = f"technical_{ticker}.json"
            if ask_gpt_to_buy(ticker, tech_file, news):
                print(f"✅ {ticker} empfohlen!")
                chosen_stocks.append(ticker)
            else:
                print(f"❌ {ticker} abgelehnt.")
        except Exception as e:
            print(f"⚠️ Fehler bei {ticker}: {e}")

        if len(chosen_stocks) >= 3:
            break

    if chosen_stocks:
        print(f"\n📈 Empfohlene Aktien: {chosen_stocks}")
        # buy_stocks(chosen_stocks)  # Auskommentiert für Tests
    else:
        print("\n❌ Keine geeigneten Aktien gefunden.")
