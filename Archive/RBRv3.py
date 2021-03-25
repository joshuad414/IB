from ib_insync import *
import pandas as pd

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)

#equities
spy = 'SPY'
qqq = 'QQQ'
aapl = 'AAPL'
msft = 'MSFT'
nio = 'NIO'
amd = 'AMD'
nvda = 'NVDA'
ba = 'BA'
cciv = 'CCIV'
baba = 'BABA'
nke = 'NKE'
dis = 'DIS'
fb = 'FB'
oxy = 'OXY'
gme = 'GME'
twtr = 'TWTR'
tsla = 'TSLA'


stock_list = []
stock_list.append(qqq)
stock_list.append(aapl)
stock_list.append(msft)
stock_list.append(nio)
stock_list.append(amd)
stock_list.append(nvda)
stock_list.append(ba)
stock_list.append(cciv)
stock_list.append(baba)
stock_list.append(nke)
stock_list.append(dis)
stock_list.append(fb)
stock_list.append(oxy)
stock_list.append(gme)
stock_list.append(twtr)
stock_list.append(tsla)


rally_percentage = 0.0008
basing_percentage = 0.9


def on_bar_update(bars: BarDataList, has_new_bar: bool):
    if has_new_bar:
        df3 = util.df(bars)
        update_rbr_data(df3)
        df3.to_csv('historical_data.csv')


def update_rbr_data(df3):
    df2 = df3
    for x in stock_list:
        a = Stock(x, 'SMART', 'USD')
        bars = ib.reqHistoricalData(a, endDateTime='', durationStr='1 D', barSizeSetting='1 min',
                                    whatToShow='MIDPOINT', useRTH=False, keepUpToDate=True)
        df = util.df(bars)
        df.drop(['volume', 'average', 'barCount'], axis=1, inplace=True)
        df['date'] = df['date'].dt.strftime('%H:%M')
        df['open_close'] = (df['close'].values - df['open'].values) / df['open'].values
        df['open_high'] = (df['high'].values - df['open'].values) / df['open'].values
        df['high1'] = df['high'].shift().values
        df['high2'] = df['high'].shift(periods=2).values
        df['high_high'] = (df['high'].values > df['high1'].values) & (df['high'].values > df['high2'].values)
        df['rally'] = df['open_close'].values > rally_percentage
        df['rally2'] = df['high_high'].values == True
        df['base'] = ((df['rally'].shift().values == True) | (df['rally2'].shift().values == True)) \
                     & ((abs(df['open_close'].values) / abs(df['open_close'].shift().values)) < basing_percentage) \
                     & (df['open_close'].values < 0)
        df['rbr'] = (df['rally2'].values == True) \
                    & (df['base'].shift().values == True) \
                    & (df['rally'].shift(periods=2).values == True)
        df['rbr2'] = (df['rbr'].values == True) \
                     | (df['rbr'].shift(periods=-1).values == True) \
                     | (df['rbr'].shift(periods=-2).values == True)
        df['onWatch'] = (df['open_close'].values < 0) \
                        & (df['rally'].shift().values == True) \
                        & ((abs(df['open_close'].values) / abs(df['open_close'].shift().values)) < basing_percentage)
        df['Symbol'] = x
        df['bar1'] = ((df['rally'].values == True) & (df['open_close'].shift().values > 0)) * 1
        df['bar2'] = ((df['bar1'].values == True) & (df['rally'].values == True) & (
                    df['open_close'].shift(periods=2).values > 0)) * 1
        df['bar3'] = ((df['bar2'].values == True) & (df['rally'].values == True) & (
                    df['open_close'].shift(periods=3).values > 0)) * 1
        df['bar4'] = ((df['bar3'].values == True) & (df['rally'].values == True) & (
                    df['open_close'].shift(periods=4).values > 0)) * 1
        df['bar5'] = ((df['bar4'].values == True) & (df['rally'].values == True) & (
                    df['open_close'].shift(periods=5).values > 0)) * 1
        df['bar'] = (df['bar1'].values + df['bar2'].values + df['bar3'].values + df['bar4'].values + df['bar5'].values)
        df2 = df2.append(df)


# Stock Ticker Data
stock = Stock('SPY', 'SMART', 'USD')
market_data = ib.reqMktData(stock, '', False, False)

bar = ib.reqHistoricalData(Stock('SPY', 'SMART', 'USD'), endDateTime='', durationStr='1 D',
                         barSizeSetting='1 min', whatToShow='MIDPOINT', useRTH=False, keepUpToDate=True)

def on_pending_ticker(ticker):
    df = util.df(bar)
    last_price = market_data.last
    print(last_price)


ib.barUpdateEvent += on_bar_update
ib.pendingTickersEvent += on_pending_ticker
ib.run()