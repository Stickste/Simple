import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
from ta.trend import MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator

def get_technical_summary(ticker: str, filename: str = "technical_summary.json") -> str:
    try:
        data = yf.download(ticker, period="6mo", interval="1d", auto_adjust=False)
        data.dropna(inplace=True)

        close = data["Close"].values.flatten()
        volume = data["Volume"].values.flatten()
        index = data.index

        data["SMA14"] = pd.Series(close).rolling(window=14).mean().values
        data["EMA14"] = pd.Series(close).ewm(span=14, adjust=False).mean().values
        data["SMA50"] = pd.Series(close).rolling(window=50).mean().values

        macd = MACD(close=pd.Series(close))
        data["MACD"] = pd.Series(macd.macd().values.flatten(), index=index)
        data["MACD_signal"] = pd.Series(macd.macd_signal().values.flatten(), index=index)
        data["MACD_hist"] = data["MACD"] - data["MACD_signal"]
        data["macd_bullish"] = data["MACD"] > data["MACD_signal"]

        rsi = RSIIndicator(close=pd.Series(close), window=14)
        data["RSI14"] = pd.Series(rsi.rsi().values.flatten(), index=index)

        bb = BollingerBands(close=pd.Series(close), window=20, window_dev=2)
        data["BB_upper"] = pd.Series(bb.bollinger_hband().values.flatten(), index=index)
        data["BB_lower"] = pd.Series(bb.bollinger_lband().values.flatten(), index=index)

        obv = OnBalanceVolumeIndicator(close=pd.Series(close), volume=pd.Series(volume))
        data["OBV"] = pd.Series(obv.on_balance_volume().values.flatten(), index=index)

        data.dropna(inplace=True)
        latest = data.iloc[[-1]]

        date = latest.index[0].strftime("%Y-%m-%d")
        summary = {
            date: {
                "Close": round(float(latest["Close"].iloc[0]), 2),
                "SMA14": round(float(latest["SMA14"].iloc[0]), 2),
                "SMA50": round(float(latest["SMA50"].iloc[0]), 2),
                "RSI14": round(float(latest["RSI14"].iloc[0]), 2),
                "MACD": round(float(latest["MACD"].iloc[0]), 3),
                "MACD_signal": round(float(latest["MACD_signal"].iloc[0]), 3),
                "MACD_hist": round(float(latest["MACD_hist"].iloc[0]), 3),
                "OBV": int(latest["OBV"].iloc[0]),
                "macd_bullish": bool(latest["macd_bullish"].iloc[0])
            }
        }

        # Load existing file or start fresh
        if os.path.exists(filename):
            with open(filename, "r") as f:
                all_data = json.load(f)
        else:
            all_data = {}

        # Update this ticker
        all_data[ticker.upper()] = summary

        # Save updated dictionary
        with open(filename, "w") as f:
            json.dump(all_data, f, indent=2)

        print(f"✅ Appended {ticker.upper()} to {filename}")
        return filename

    except Exception as e:
        print(f"❌ Error with {ticker.upper()}: {e}")
        return ""

if __name__ == "__main__":
    get_technical_summary("TSLA")
    get_technical_summary("AAPL")