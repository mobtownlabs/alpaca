from datetime import datetime

from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers import Alpaca
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
import config


class MyStrategy(Strategy):
    # Custom parameters
    parameters = {
        "symbol": "BTC/USD",
        "quantity": 0.00001,
        "side": "buy"
    }

    def initialize(self, symbol=""):
        # Will make on_trading_iteration() run every 10 minutes
        self.sleeptime = "10M"

    def on_trading_iteration(self):
        symbol = self.parameters["symbol"]
        quantity = self.parameters["quantity"]
        side = self.parameters["side"]

        order = self.create_order(symbol, quantity, side)
        self.submit_order(order)


trader = Trader()
broker = Alpaca(config.ALPACA_CONFIG)
strategy = MyStrategy(
    broker=broker,
    parameters= {
        "symbol": "BTC/USD"
    })

# Backtest this strategy
backtesting_start = datetime(2023, 1, 1)
backtesting_end = datetime(2023, 12, 26)
strategy.backtest(
    YahooDataBacktesting,
    backtesting_start,
    backtesting_end,
    # You can also pass in parameters to the backtesting class, this will override the parameters in the strategy
    parameters= {
        "symbol": "BTC/USD"
    },
)

# Run the strategy live
trader.add_strategy(strategy)
trader.run_all()