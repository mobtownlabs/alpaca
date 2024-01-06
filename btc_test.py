from datetime import datetime

from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers import Alpaca
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from lumibot.entities import Asset
import config



class MyStrategy(Strategy):

    def initialize(self, force_start_immidiately=True):
        #self.get_account = self.broker.get_account  # Add this line to define the get_account method
        # Will make on_trading_iteration() run every 180 minutes
        self.set_market('24/7')
        self.sleeptime = "10S" #default is 5 minutes
        

    def on_trading_iteration(self):      
        symbol = Asset(symbol = "BTC", asset_type="crypto")
        quote = Asset(symbol = "USDT", asset_type="crypto")
        quantity = 100000 * 0.1 / self.get_last_price(symbol, quote=quote)
        side = 'buy'
        type = 'limit'
        limit_price = self.get_last_price(symbol, quote=quote) * 0.999

        order = self.create_order(symbol, quantity, side, limit_price=limit_price, type=type)
        self.submit_order(order)
        del quantity, limit_price 
    
    def on_partially_filled_order(self, position, order, price, quantity, multiplier):
        return super().on_partially_filled_order(position, order, price, quantity, multiplier)

trade = True
if trade:
    broker = Alpaca(config.ALPACA_CONFIG)
    strategy = MyStrategy(broker=broker)
    for order in strategy.get_orders():
        order.log_message(order)
    trader = Trader()
    trader.add_strategy(strategy)
    trader.run_all()
else:
    print('something went wrong')
