from ib_insync import *

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

stock_list = []
stock_list.append(aapl)
stock_list.append(msft)

rally_percentage = 0.0008
basing_percentage = 0.9  # basing candle open close percentage of previous rally candle

stock = aapl
stock = Stock(stock, 'SMART', 'USD')


bar = ib.reqHistoricalData(stock, endDateTime='', durationStr='1 D', barSizeSetting='5 mins',
                           whatToShow='MIDPOINT', useRTH=True, keepUpToDate=True)


def on_bar_update(bars: BarDataList, has_new_bar: bool):
    if has_new_bar:
        df2 = util.df(bars)


def update_rbr_data(df):
    df.drop(['volume', 'average', 'barCount'], axis=1, inplace=True)
    df['date'] = df['date'].dt.strftime('%H:%M')
    df['open_close'] = (df['close'].values-df['open'].values)/df['open'].values
    df['open_high'] = (df['high'].values-df['open'].values)/df['open'].values
    df['high1'] = df['high'].shift().values
    df['high2'] = df['high'].shift(periods=2).values
    df['high_high'] = (df['high'].values > df['high1'].values) & (df['high'].values > df['high2'].values)
    df['rally'] = df['open_close'].values > rally_percentage
    df['rally2'] = df['high_high'].values == True
    df['base'] = ((df['rally'].shift().values == True) | (df['rally2'].shift().values == True)) \
                 & ((abs(df['open_close'].values) / abs(df['open_close'].shift().values)) < basing_percentage)\
                 & (df['open_close'].values < 0)
    df['rbr'] = (df['rally2'].values == True) \
                 & (df['base'].shift().values == True) \
                 & (df['rally'].shift(periods=2).values == True)
    df['rbr2'] = (df['rbr'].values == True) \
                 | (df['rbr'].shift(periods=-1).values == True) \
                 | (df['rbr'].shift(periods=-2).values == True)
    df['onWatch'] = (df['open_close'].values < 0) \
                 & (df['rally'].shift().values == True) \
                 & ((abs(df['open_close'].values) / abs(df['open_close'].shift().values))<basing_percentage)
    df['bar1'] = ((df['rally'].values == True) & (df['open_close'].shift().values > 0))*1
    df['bar2'] = ((df['bar1'].values == True) & (df['rally'].values == True) & (df['open_close'].shift(periods=2).values > 0))*1
    df['bar3'] = ((df['bar2'].values == True) & (df['rally'].values == True) & (df['open_close'].shift(periods=3).values > 0))*1
    df['bar4'] = ((df['bar3'].values == True) & (df['rally'].values == True) & (df['open_close'].shift(periods=4).values > 0))*1
    df['bar5'] = ((df['bar4'].values == True) & (df['rally'].values == True) & (df['open_close'].shift(periods=5).values > 0))*1
    df['bar'] = (df['bar1'].values + df['bar2'].values + df['bar3'].values + df['bar4'].values + df['bar5'].values)
    df = df.drop(columns=['open_close', 'open_high', 'high1', 'high2', 'high_high', 'base', 'rally', 'rally2', 'rbr', 'bar1', 'bar2', 'bar3', 'bar4', 'bar5'])
    df = df.rename(columns={'rbr2': 'rbr'})
    df['Symbol'] = aapl
    df_rbr = df[df['rbr'] != False]
    df.to_csv('historical_data.csv')
    df_rbr.to_csv('rbr.csv')


# Stock Ticker Data
market_data = ib.reqMktData(stock, '', False, False)


def on_pending_ticker(ticker):
    df = util.df(bar)
    update_rbr_data(df)
    last_price = market_data.last


ib.barUpdateEvent += on_bar_update
ib.pendingTickersEvent += on_pending_ticker
ib.run()