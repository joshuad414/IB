from ib_insync import *
import pandas as pd


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=5)

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
twtr = 'TWTR'
tsla = 'TSLA'


stock_list = []
stock_list.append(spy)
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
stock_list.append(twtr)
stock_list.append(tsla)


rally_percentage = 0.0008
basing_percentage = 0.9
bar_time_frame = '5 mins'
rt_hours = True

pd.options.display.float_format = '{:.2f}'.format
df2 = pd.DataFrame()

for x in stock_list:
    stock = Stock(x, 'SMART', 'USD')
    bars = ib.reqHistoricalData(stock, endDateTime='', durationStr='1 D', barSizeSetting=bar_time_frame,
                                whatToShow='MIDPOINT', useRTH=rt_hours, keepUpToDate=True)
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
    df['bar2'] = ((df['bar1'].values == True) & (df['rally'].values == True) & (df['open_close'].shift(periods=2).values > 0)) * 1
    df['bar3'] = ((df['bar2'].values == True) & (df['rally'].values == True) & (df['open_close'].shift(periods=3).values > 0)) * 1
    df['bar4'] = ((df['bar3'].values == True) & (df['rally'].values == True) & (df['open_close'].shift(periods=4).values > 0)) * 1
    df['bar5'] = ((df['bar4'].values == True) & (df['rally'].values == True) & (df['open_close'].shift(periods=5).values > 0)) * 1
    df['bar'] = (df['bar1'].values + df['bar2'].values + df['bar3'].values + df['bar4'].values + df['bar5'].values)
    df['basing_percent'] = abs(df['open_close'].values) / abs(df['open_close'].shift().values)
    df2 = df2.append(df)

# df2 = df2.drop(columns=['open_close', 'open_high', 'high1', 'high2', 'high_high', 'base', 'rally', 'rally2', 'rbr', 'bar1', 'bar2', 'bar3', 'bar4', 'bar5'])
df2 = df2.drop(columns=['rbr'])
df2 = df2.rename(columns={'rbr2': 'rbr'})
df2.to_csv('dist/historical_data.csv')
df_rbr = df2[df2['rbr'] != False]
df_rbr.to_csv('dist/rbr.csv')