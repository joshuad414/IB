from ib_insync import *
import time
import pandas as pd
import numpy as np

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)

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

# stock to watch
stock = aapl
stock = Stock(stock, 'SMART', 'USD')

# create initial df to create 5 minute bar values to detect RBR
#bars = ib.reqHistoricalData(
#    stock, endDateTime='', durationStr='1 D',
#    barSizeSetting='5 mins', whatToShow='MIDPOINT', useRTH=True)
#df = util.df(bars)

# makeshift data
data = [['3/15/2021  8:30:00 AM', 315.815, 315.815, 314.575, 315.205,'','',''],
        ['3/15/2021  8:35:00 AM', 315.205, 315.755, 314.765, 314.935,'','',''],
        ['3/15/2021  8:40:00 AM', 314.935, 315.315, 314.515, 315.145,'','',''],
        ['3/15/2021  8:45:00 AM', 315.145, 315.58, 314.845, 315.235,'','',''],
        ['3/15/2021  8:50:00 AM', 315.235, 316.385, 315.165, 316.105,'','',''],
        ['3/15/2021  8:55:00 AM', 316.105, 316.595, 315.685, 316.075,'','',''],
        ['3/15/2021  9:00:00 AM', 316.075, 316.745, 315.94, 316.525,'','','']]
df = pd.DataFrame(data, columns=['date','open','high','low','close','volume', 'average', 'barCount'])

# go through df to create/identify RBR rows
df.drop(['volume', 'average', 'barCount'], axis=1, inplace=True)
df['open_close'] = (df['close'].values - df['open'].values) / df['open'].values
df['open_high'] = (df['high'].values - df['open'].values) / df['open'].values
df['high1'] = df['high'].shift().values
df['high2'] = df['high'].shift(periods=2).values
df['high_high'] = (df['high'].values > df['high1'].values) & (df['high'].values > df['high2'].values)
df['rally'] = df['open_close'].values > 0.001
df['base'] = (df['open_close'].values < 0) \
             & (df['high_high'].shift(periods=-1).values == True) \
             & ((df['rally'].shift().values == True) | (df['high_high'].values == True)) \
             & ((abs(df['open_close'].values) / abs(df['open_close'].shift().values)) < 0.4)
df['rally2'] = df['high_high'].values == True
df['rbr'] = (df['rally2'].values == True) \
            & (df['base'].shift().values == True) \
            & (df['rally'].shift(periods=2).values == True)
df['rbr2'] = (df['rbr'].values == True) \
             | (df['rbr'].shift(periods=-1).values == True) \
             | (df['rbr'].shift(periods=-2).values == True)
df['onWatch'] = (df['open_close'].values < 0) \
                & (df['rally'].shift().values == True) \
                & ((abs(df['open_close'].values) / abs(df['open_close'].shift().values)) < 0.4)

# get market data for stock
# market_data = ib.reqMktData(stock, '', False, False)

# create method to pull live ticker data and compare it to previous bar high value and buy/sell
def onPendingTicker(shares_buy):
    last = 136.00
    #last = market_data.last                 # get last ticker price
    base_high = df['high'].values[-2]       # high value from last closed candle
    watching = df['onWatch'].values[-2]     # pulls boolean from onWatch column for the last closed candle
    basing_open = df['base'].values[-2]     # pulls boolean from base column for the last closed candle
    minute = time.localtime().tm_min        # gets current minute

    if (last > base_high) & (watching == True):         # checks if last ticker price is greater than the basing candles high value and that we are on watch
        count = 0                                       # creates count for number of trades executed
        #print(last, base_high, 'yes', minute)
        buy = MarketOrder('BUY', shares_buy)        # creates buy Market Order
        trade = ib.placeOrder(stock, buy)               # places order to buy shares_buy for stock
        print('Trade Executed')
        ib.sleep(1)
        executed_trades = ib.reqExecutions()            # pulls executed trades from IB
        count +=1                               # adds 1 to executed trade count
        while i < len(executed_trades):
            if i == (count-1):
                executed_trade_price = executed_trades[i][1].price     # gets executed trade price for current trade (count)
                break                                   # breaks while loop
            i += 1
        if last < basing_open:                          # if the last ticker price is less than the basing candle open sell position
            sell = MarketOrder('SELL', shares_buy)
            trade = ib.placeOrder(stock, sell)
        elif (last * 1.0001) > executed_trade_price:    # if the last ticker price is greater than x % of trade price, sell 20% of position
            sell = MarketOrder('SELL', shares_buy*.2)
            trade = ib.placeOrder(stock, sell)
            shares_buy = shares_buy - (shares_buy*.2)
        elif (last * 1.0002) > executed_trade_price:    # if the last ticker price is greater than x % of trade price, sell 20% of position
            sell = MarketOrder('SELL', shares_buy*.2)
            trade = ib.placeOrder(stock, sell)
            shares_buy = shares_buy - (shares_buy * .4)
        elif (last * 1.0003) > executed_trade_price:    # if the last ticker price is greater than x % of trade price, sell 20% of position
            sell = MarketOrder('SELL', shares_buy*.2)
            trade = ib.placeOrder(stock, sell)
            shares_buy = shares_buy - (shares_buy * .6)
        elif (last * 1.0004) > executed_trade_price:    # if the last ticker price is greater than x % of trade price, sell 20% of position
            sell = MarketOrder('SELL', shares_buy*.2)
            trade = ib.placeOrder(stock, sell)
            shares_buy = shares_buy - (shares_buy * .8)
        elif (last * 1.0005) > executed_trade_price:    # if the last ticker price is greater than x % of trade price, sell 20% of position
            sell = MarketOrder('SELL', shares_buy*.2)
            trade = ib.placeOrder(stock, sell)
    else:
        1 == 1
       #print(last, base_high, 'no', minute)


ib.pendingTickersEvent += onPendingTicker(shares_buy)
ib.run()