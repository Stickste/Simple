import alpaca_trade_api as tradeapi
import os
alp_key = os.getenv("ALPACA_API_KEY")
alp_secret = os.getenv("ALPACA_SECRET_KEY")

api = tradeapi.REST(alp_key, alp_secret, "https://paper-api.alpaca.markets")
