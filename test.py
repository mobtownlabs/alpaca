from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.stream import TradingStream
import config


client = TradingClient(config.API_KEY, config.SECRET_KEY, paper=False)


account = dict(client.get_account())

for k,v in account.items():
    print(f"{k:30}: {v}")


order_details = MarketOrderRequest(
    symbol = "BTC/USD",
    qty = 0.0000995,
    side = OrderSide.SELL,
    type = "market",
    time_in_force = "gtc"
)

order = client.submit_order(order_details)

trades = TradingStream(config.API_KEY, config.SECRET_KEY, paper=False)  

async def trade_status(data):
    print(data)
    
trades.subscribe_trade_updates(trade_status)
trades.run()

assets = [asset for asset in client.get_all_positions()]
positions = [(asset.symbol, asset.qty, asset.current_price) for asset in assets]

for position in positions:
    print(f"{position[0]:9}{position[1]:>4}{float(position[1]) * float(position[2]):>15.2f}")
    
client.close_all_positions(cancel_orders=True)

exit()


