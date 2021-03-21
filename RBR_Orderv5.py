from ib_insync import *
import time
import pandas as pd
import numpy as np

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# equities
spy = 'SPY'
qqq = 'QQQ'
aapl = 'AAPL'
msft = 'MSFT'
nio = 'NIO'
amd = 'AMD'
nvda = 'NVDA'
ba = 'BA'

# Variables
shares_buy = 100
shares_sold = shares_buy * 0.2
total_shares_sold = 0
total_shares_remain = shares_buy
time_threshold = 240
sell_1_price = 1.025
sell_2_price = 1.05
sell_3_price = 1.1
sell_4_price = 1.15
sell_5_price = 1.2
rally_percentage = 0.0008 # rally percentage from open to close of 1st rally candle
basing_percentage = 0.9  # basing candle percentage from open to close of previous rally candle

# equity to watch
stock = spy
stock = Stock(stock, 'SMART', 'USD')

# Get Historical Ticker Data
bar = ib.reqHistoricalData(stock, endDateTime='', durationStr='1 D', barSizeSetting='1 min',
                           whatToShow='MIDPOINT', useRTH=True, keepUpToDate=True)


def on_bar_update(bars: BarDataList, has_new_bar: bool):
    if has_new_bar:
        newdf = util.df(bars)


# get market data for stock
market_data = ib.reqMktData(stock, '', False, False)


# method to pull live ticker data and compare it to previous bar high value and buy/sell
def on_pending_ticker(ticker):
    df = util.df(bar)
    base_high = df['high'].values[-2]                   # high value from basing candle
    watching = df['onWatch'].values[-2]                 # pulls boolean from onWatch column for the last closed candle
    basing_open = df['base'].values[-2]                 # pulls boolean from base column for the last closed candle
    last_price = market_data.last                       # get last ticker price
    # check if last price is above vwap
    day_value = last_price - df['open'].values[0]       # check if stock is positive or negative for the day

    if (last_price > base_high) & (watching == True):
        count = 0                                       # creates count for number of trades executed
        buy_market = MarketOrder('BUY', shares_buy)     # creates buy Market Order
        trade = ib.placeOrder(stock, buy_market)        # places order to buy shares for stock
        t0 = time.time()
        ib.sleep(1)
        executed_trades = ib.reqExecutions()            # pulls list of executed trades from IB
        count += 1                                      # adds 1 to executed trade count

        last_price = market_data.last                   # get last ticker price
        # may need to remove and set executed trade
        # price to last market data price at time of stock buy
        i = 1
        while i < len(executed_trades):
            if i == (count-1):
                executed_trade_price = executed_trades[i][1].price
                print('Buy Executed:', shares_buy, stock, "@", executed_trade_price)
                break
            i += 1
        while last_price > basing_open:
            t1 = time.time()
            total_time = t1 - t0
            if (total_time > time_threshold) & (last_price < base_high):
                remaining_shares = shares_buy - total_shares_sold
                sell = MarketOrder('SELL', remaining_shares)
                trade = ib.placeOrder(stock, sell)
                total_shares_remain = 0
                print('Sell Executed:', remaining_shares, stock, "@", executed_trade_price)
                break
            elif (last_price * sell_1_price) > executed_trade_price:
                sell = MarketOrder('SELL', shares_sold)
                trade = ib.placeOrder(stock, sell)
                total_shares_sold = shares_sold
                total_shares_remain = shares_buy - total_shares_sold
                print('Sell Executed:', shares_sold, stock, "@", executed_trade_price)
            elif (last_price * sell_2_price) > executed_trade_price:
                sell = MarketOrder('SELL', shares_sold*2)
                trade = ib.placeOrder(stock, sell)
                total_shares_sold = shares_sold * 2
                total_shares_remain = shares_buy - total_shares_sold
                print('Sell Executed:', shares_sold*2, stock, "@", executed_trade_price)
            elif (last_price * sell_3_price) > executed_trade_price:
                sell = MarketOrder('SELL', shares_sold*3)
                trade = ib.placeOrder(stock, sell)
                total_shares_sold = shares_sold * 3
                total_shares_remain = shares_buy - total_shares_sold
                print('Sell Executed:', shares_sold*3, stock, "@", executed_trade_price)
            elif (last_price * sell_4_price) > executed_trade_price:
                sell = MarketOrder('SELL', shares_sold*4)
                trade = ib.placeOrder(stock, sell)
                total_shares_sold = shares_sold * 4
                total_shares_remain = shares_buy - total_shares_sold
                print('Sell Executed:', shares_sold*4, stock, "@", executed_trade_price)
            elif (last_price * sell_5_price) > executed_trade_price:
                sell = MarketOrder('SELL', shares_sold*5)
                trade = ib.placeOrder(stock, sell)
                total_shares_sold = shares_sold * 5
                total_shares_remain = shares_buy - total_shares_sold
                print('Sell Executed:', shares_sold*5, stock, "@", executed_trade_price)
                break
        if (total_shares_remain != 0):
            sell = MarketOrder('SELL', total_shares_remain)
            trade = ib.placeOrder(stock, sell)
            print('Sell Executed:', total_shares_remain * 5, stock, "@", executed_trade_price)
    else:
        print('Last Price:', last_price, ', Basing Candle High:', base_high)

ib.barUpdateEvent += on_bar_update
ib.pendingTickersEvent += on_pending_ticker
ib.run()