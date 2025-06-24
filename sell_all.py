# sell_all.py
import os
import alpaca_trade_api as tradeapi

alp_key = os.getenv("APCA_API_KEY_ID")
alp_secret = os.getenv("APCA_API_SECRET_KEY")
base_url = "https://paper-api.alpaca.markets"

api = tradeapi.REST(alp_key, alp_secret, base_url)

def sell_all_positions():
    try:
        positions = api.list_positions()
        if not positions:
            print("📭 Keine offenen Positionen.")
            return

        print(f"🧹 Verkaufe {len(positions)} Position(en)...")
        for position in positions:
            api.submit_order(
                symbol=position.symbol,
                qty=position.qty,
                side="sell",
                type="market",
                time_in_force="day"
            )
            print(f"✅ Verkauf eingereicht: {position.symbol} ({position.qty} Stück)")
    except Exception as e:
        print(f"❌ Fehler beim Verkauf: {e}")

if __name__ == "__main__":
    sell_all_positions()