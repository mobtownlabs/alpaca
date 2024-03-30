from datetime import datetime

from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers import Ccxt
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from lumibot.entities import Asset
import config



class MyStrategy(Strategy):
    data =[]
    order_number = 0
    def initialize(self, force_start_immidiately=True):
        #self.get_account = self.broker.get_account  # Add this line to define the get_account method
        # Will make on_trading_iteration() run every 180 minutes
        self.set_market('24/7')
        self.sleeptime = "10S" #default is 5 minutes
        

    def on_trading_iteration(self):      
        symbol = Asset(symbol = "BTC", asset_type="crypto")
        quote = Asset(symbol = "USD", asset_type="forex")
        entry_price = self.get_last_price(symbol)
        self.log_message(f"This is the entry price: {entry_price}")
        self.log_message(f"This is the price of the last trade: {self.get_last_price(symbol)}")
        self.log_message(f"Position: {self.get_position(symbol)}")
        self.data.append(self.get_last_price(symbol))
        self.log_message(f"Last price: {self.data[-1]}")
        self.log_message(f"Last 3 prints: {self.data[-3:]}")
        if len(self.data) > 3:
            temp = self.data[-3:]
            if temp[-1] > temp[1] > temp[0]:
                self.log_message(f"Last 3 prints: {temp}")
                quantity = 10000 * 0.1 / temp[-1]
                side = 'buy'
                #type = 'limit'
                #limit_price = self.get_last_price(symbol, quote=quote) * 0.999

                order = self.create_order(symbol, quantity, side)
                self.submit_order(order)
                self.order_number += 1
                if self.order_number == 1:
                    self.log_message(f"Entry price: {temp[-1]}")
                    entry_price = temp[-1]
            if self.get_position(symbol) and self.data[-1] < entry_price * 0.995:
                self.sell_all()
                self.order_number = 0
            elif self.get_position(symbol) and self.data[-1] >= entry_price * 1.015:
                self.sell_all()
                self.order_number = 0

trade = True
if trade:
    broker = Ccxt(config.KRAKEN_CONFIG)
    strategy = MyStrategy(broker=broker)
    trader = Trader()
    trader.add_strategy(strategy)
    trader.run_all()
else:
    print('something went wrong')
