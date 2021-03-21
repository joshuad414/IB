from ib_insync import *
import time
import numpy as np

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# equities
spy = 'SPY'
qqq = 'QQQ'
aapl = 'AAPL'

stock = aapl

stock = Stock(stock, 'SMART', 'USD')

bar = ib.reqHistoricalData(stock, endDateTime='', durationStr='1 D', barSizeSetting='1 min',
                           whatToShow='MIDPOINT', useRTH=True, keepUpToDate=True)


def on_bar_update(bars: BarDataList, has_new_bar: bool):
    if has_new_bar:
        df2 = util.df(bars)


# option data
strike_price = 120
option_month = str(time.localtime().tm_mon)
option_year = str(time.localtime().tm_year)
if len(option_month) == 1:
    option_month = '0' + option_month
option_contract = Option(aapl, '20210401', strike_price, 'C', 'SMART', '100', 'USD')

# Stock Ticker Data
market_data = ib.reqMktData(stock, '', False, False)


def on_pending_ticker(ticker):
    df = util.df(bar)
    open_candle = df['open'][len(df) - 2]
    time_candle = df['date'][len(df) - 2]
    last_price = market_data.last
    print(aapl, 'Last Price:', last_price, open_candle)
    # if last_price >= 120.38:
    #    mark_order = MarketOrder('BUY', 1)
    #    trade = ib.placeOrder(option_contract, mark_order)
    #    ib.disconnect()
    #    print('Order Filled')


ib.barUpdateEvent += on_bar_update
ib.pendingTickersEvent += on_pending_ticker
ib.run()
