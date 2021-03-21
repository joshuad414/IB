from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)
#ib.run()

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

rally_percentage = 0.0008
basing_percentage = 0.9  # basing candle open close percentage of previous rally candle

stock = aapl
bars = ib.reqHistoricalData(
    Stock(stock, 'SMART', 'USD'), endDateTime='', durationStr='2 D',
    barSizeSetting='5 mins', whatToShow='MIDPOINT', useRTH=True
)

df = util.df(bars)
df.drop(['volume', 'average', 'barCount'], axis=1, inplace=True)

df['open_close'] = (df['close'].values-df['open'].values)/df['open'].values
df['open_high'] = (df['high'].values-df['open'].values)/df['open'].values
df['high1'] = df['high'].shift().values
df['high2'] = df['high'].shift(periods=2).values
df['high_high'] = (df['high'].values > df['high1'].values) & (df['high'].values > df['high2'].values)
df['rally'] = df['open_close'].values > rally_percentage
df['base'] = (df['open_close'].values < 0) \
             & (df['high_high'].shift(periods=-1).values == True) \
             & ((df['rally'].shift().values == True) | (df['high_high'].values == True)) \
             & ((abs(df['open_close'].values) / abs(df['open_close'].shift().values))<basing_percentage)
df['rally2'] = df['high_high'].values == True
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
df['Symbol'] = stock
df_rbr = df[df['rbr'] != False]
df.to_csv('historical_data.csv')
df_rbr.to_csv('rbr.csv')