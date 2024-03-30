from datetime import datetime, timedelta

from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers import Alpaca
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from lumibot.entities import Asset
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest
import config

"""
First check if there are buy orders filled within the past 90 seconds.  
If so, grab the price of the last filled or partially filled order.
Set that last price as the starting price.
if starting price is non-zero, run every XX seconds (10 or 30) and log the current price of the asset
    if the last 3 prices are descending
        buy X% of of portfolio value / current price units of the asset
    if starting price is 0.02% above the current price, sell all units of the asset
    else if starting price is 0.01% below the current price, sell all units of the asset
Else, proceed with no starting price.
    start logging the current price of the asset every XX seconds (10 or 30)
    if the last 3 prices are descending
        buy X% of of portfolio value / current price units of the asset
 
"""
class MyStrategy(Strategy):
    data =[]
    order_time = datetime.now() + timedelta(seconds=100)
    def initialize(self, force_start_immidiately=True):
        #self.get_account = self.broker.get_account  # Add this line to define the get_account method
        # Will make on_trading_iteration() run every 180 minutes
        self.set_market('24/7')
        self.sleeptime = "30S" #default is 5 minutes
    
    def on_partially_filled_order(self, position, order, price, quantity, multiplier):
        order_time = datetime.now()
    
    def on_filled_order(self, position, order, price, quantity, multiplier):
        order_time = datetime.now()
        
    def on_trading_iteration(self):
        #get all orders
        entry_price = 0
        orders = self.get_orders()
        #loop through orders and find the last filled order
        for order in orders:
            #if the order was filled within the past 90 seconds, set the entry price to the fill price
            if order.is_filled() and (datetime.now() - order_time).total_seconds() < 90:
                #set the entry price to the fill price for a recently filled order
                entry_price = order.get_fill_price()
                self.log_message(f"Entry price was pulled from Order {order.id}: {entry_price}")
                break
        symbol = Asset(symbol = "BTC", asset_type="crypto")
        quote = Asset(symbol = "USD", asset_type="forex")
        total_budget = 100000
        
        client = CryptoHistoricalDataClient()
        request_params = CryptoLatestQuoteRequest(symbol_or_symbols="BTC/USD")
        latest_quote = client.get_crypto_latest_quote(request_params)
        alpaca_quote = latest_quote["BTC/USD"].ask_price
        quantity = total_budget * 0.1 / alpaca_quote
        #if there was no recently filled order, set the entry price to the last quote from aplaca
        if entry_price == 0:
            entry_price = alpaca_quote
            self.log_message(f"Entry price is the Alpaca recent Quote : {entry_price}")
        
        self.log_message(f"This is the position value: {self.portfolio_value - self.cash}")
        if self.get_position(symbol):
            self.log_message(f"This is the position quantity: {self.get_position(symbol).quantity}")
        else:
            self.log_message(f"There is no position")
        self.log_message(f"This is the alpaca quote price: {alpaca_quote}")
        self.log_message(f"Position: {self.get_position(symbol)}")
        self.data.append(latest_quote["BTC/USD"].ask_price)
        self.log_message(f"Last price logged: {self.data[-1]}")
        self.log_message(f"Last 3 prints: {self.data[-3:]}")
        if len(self.data) > 3:
            temp = self.data[-3:]
            if temp[-1] < temp[1] <= temp[0]:
                #if there's a declining trend for the past 90 seconds (3 iterations) buy 10% of the portfolio value
                #but buy at a price that's 0.2% below the current price
                self.log_message(f"Last 3 prints: {temp}")
                side = 'buy'
                type = 'limit'
                limit_price = latest_quote["BTC/USD"].ask_price * 0.998
                order = self.create_order(symbol, quantity, side, type=type, limit_price=limit_price)
                self.submit_order(order)
                self.order_number += 1
            #if the last price is 0.1% below the entry price, sell all units of the asset at a price that's 0.1% below the entry price
            if self.get_position(symbol) and self.data[-1] < entry_price * 0.999:
                quantity = self.get_position(symbol).quantity
                side = 'sell'
                type = 'limit'
                limit_price = entry_price * 0.999
                order = self.create_order(symbol, quantity, side, type=type, limit_price=limit_price)
                self.submit_order(order)
                self.order_number = 0
            #if the last price is 0.2% above the entry price, sell all units of the asset at a price that's 0.2% above the entry price
            elif self.get_position(symbol) and self.data[-1] >= entry_price * 1.002:
                quantity = self.get_position(symbol).quantity
                side = 'sell'
                type = 'limit'
                limit_price = entry_price * 1.002
                order = self.create_order(symbol, quantity, side, type=type, limit_price=limit_price)
                self.submit_order(order)
                self.order_number = 0

trade = True
if trade:
    broker = Alpaca(config.ALPACA_CONFIG)
    strategy = MyStrategy(broker=broker)
    trader = Trader()
    trader.add_strategy(strategy)
    trader.run_all()
else:
    print('something went wrong')
