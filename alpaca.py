import alpaca_trade_api as tradeapi
from Simple.keys import alp_key, alp_endpoint, alp_secret

api = tradeapi.REST(alp_key, alp_secret, alp_endpoint)
