import os

# Only load .env if not running in CI (GitHub Actions)
if not os.getenv("GITHUB_ACTIONS"):
    from dotenv import load_dotenv
    load_dotenv()

import json
import random
from datetime import datetime
from trading import buy_stocks

from yfin import get_technical_summary
from news import get_news_articles
from recommend import get_stock_decision     # ⬅️ neue Funktion liefert (bool, reason)
from sp500 import fetch_sp500_tickers


# ─────────────────────────────── Konstanten ────────────────────────────────
MAX_BUYS        = 3
TECH_FILE       = "technical_summary.json"
DECISIONS_LOG   = "decisions.log"


# ───────────────────────────── Main Pipeline ───────────────────────────────
def main():
    tickers_to_check = fetch_sp500_tickers()
    random.shuffle(tickers_to_check)                 # ▶ Zufällige Reihenfolge

    # Alte Technikal-Datei entfernen
    if os.path.exists(TECH_FILE):
        os.remove(TECH_FILE)

    # ── Technische Daten sammeln
    for ticker in tickers_to_check:
        if '.' in ticker:            # z. B. BRK.B
            continue
        get_technical_summary(ticker)

    # ── Ergebnisse laden
    if not os.path.exists(TECH_FILE):
        print("❌ Technische Daten wurden nicht gefunden.")
        return

    with open(TECH_FILE, "r", encoding="utf-8") as f:
        technical_data = json.load(f)

    chosen_stocks = []

    # ── Entscheidungs-Log vorbereiten
    with open(DECISIONS_LOG, "a", encoding="utf-8") as log_file:
        log_file.write("\n# --- Run " + datetime.now().isoformat() + " ---\n")

    # ── Screening-Schleife
    for ticker in tickers_to_check:
        if len(chosen_stocks) >= MAX_BUYS:
            break
        if ticker not in technical_data:
            continue


        # ── News + Prompt
        try:
            news = get_news_articles(ticker)
            prompt = (
                f"As a financial trading assistant, analyze the following data "
                f"and determine if buying {ticker} at market open and selling "
                f"at market close today is likely to yield a profit.\n\n"
                f"Technicals: {json.dumps(technical_data[ticker])}\n\n"
                f"News: {news}"
            )

            print(f"\n📨 Anfrage an GPT für {ticker}...")
            buy, reason = get_stock_decision(prompt)          # ⬅️ neue Rückgabe

            # ── Entscheidungs-Log
            with open(DECISIONS_LOG, "a", encoding="utf-8") as log_file:
                decision_txt = "BUY" if buy else "SKIP"
                log_file.write(f"{ticker}\t{decision_txt}\t{reason}\n")

            # ── Ergebnis
            if buy:
                chosen_stocks.append(ticker)
                print(f"✅ Kaufempfehlung für {ticker}: {reason}")
            else:
                print(f"⛔️ Keine Empfehlung für {ticker}: {reason}")

        except Exception as e:
            print(f"❌ Fehler bei {ticker}: {e}")

    # ── Ausführen
    if chosen_stocks:
        print(f"\n📈 Empfohlene Aktien: {chosen_stocks}")
        buy_stocks(chosen_stocks)          # Realen Handel aktivieren → Kommentar entfernen
    else:
        print("\n❌ Keine geeigneten Aktien gefunden.")


if __name__ == "__main__":
    main()
