from ib_insync import *
import pandas as pd
from Requirements import bar_time_frame, rt_hours, rally_percentage, basing_percentage, stock_list
import numpy as np

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=10)

df2 = pd.DataFrame()

for x in stock_list:
    print(x)
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
    with np.errstate(divide='ignore'):
        df['base'] = ((df['rally'].shift().values == True) | (df['rally2'].shift().values == True)) \
                     & ((abs(df['open_close'].values) / abs(df['open_close'].shift().values)) < basing_percentage) \
                     & (df['open_close'].values < 0)
    df['rbr'] = (df['rally2'].values == True) \
        & (df['base'].shift().values == True) \
        & (df['rally'].shift(periods=2).values == True)
    df['rbr2'] = (df['rbr'].values == True) \
        | (df['rbr'].shift(periods=-1).values == True) \
        | (df['rbr'].shift(periods=-2).values == True)
    with np.errstate(divide='ignore'):
        df['onWatch'] = (df['open_close'].values < 0) \
                        & (df['rally'].shift().values == True) \
                        & ((abs(df['open_close'].values) / abs(df['open_close'].shift().values)) < basing_percentage)
    df['Symbol'] = x
    df['bar1'] = ((df['rally'].values == True) & (df['open_close'].shift().values > 0)) * 1
    df['bar2'] = ((df['bar1'].values == True) & (df['rally'].values == True)
                  & (df['open_close'].shift(periods=2).values > 0)) * 1
    df['bar3'] = ((df['bar2'].values == True) & (df['rally'].values == True)
                  & (df['open_close'].shift(periods=3).values > 0)) * 1
    df['bar4'] = ((df['bar3'].values == True) & (df['rally'].values == True)
                  & (df['open_close'].shift(periods=4).values > 0)) * 1
    df['bar5'] = ((df['bar4'].values == True) & (df['rally'].values == True)
                  & (df['open_close'].shift(periods=5).values > 0)) * 1
    df['bar'] = (df['bar1'].values + df['bar2'].values + df['bar3'].values + df['bar4'].values + df['bar5'].values)
    with np.errstate(divide='ignore'):
        df['basing_percent'] = abs(df['open_close'].values) / abs(df['open_close'].shift().values)
    df2 = df2.append(df)

df2 = df2.drop(columns=['rbr'])
df2 = df2.rename(columns={'rbr2': 'rbr'})
df2.to_csv('dist/historical_data.csv')
df_rbr = df2[df2['rbr'] != False]
df_rbr.to_csv('dist/rbr.csv')
