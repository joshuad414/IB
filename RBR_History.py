from ib_insync import *
import pandas as pd
from Requirements import bar_time_frame_historic, rally_percentage, basing_percentage, duration, stock_list
import numpy as np
from datetime import datetime


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=5)


pd.options.display.float_format = '{:.2f}'.format
df2 = pd.DataFrame()

for x in stock_list:
    print(x)
    stock = Stock(x, 'SMART', 'USD')
    bars = ib.reqHistoricalData(stock, endDateTime='', durationStr=duration, barSizeSetting=bar_time_frame_historic,
                                whatToShow='MIDPOINT', useRTH=True, keepUpToDate=True)
    df = util.df(bars)
    df.drop(['volume', 'average', 'barCount'], axis=1, inplace=True)
    df['date'] = df['date'].dt.strftime('%m/%d/%Y')
    df['open_close'] = (df['close'].values - df['open'].values) / df['open'].values
    df['open_high'] = (df['high'].values - df['open'].values) / df['open'].values
    df['high1'] = df['high'].shift().values
    df['high2'] = df['high'].shift(periods=2).values
    df['high_high'] = (df['high'].values > df['high1'].values) & (df['high'].values > df['high2'].values)
    df['rally'] = df['open_close'].values > rally_percentage
    df['rally2'] = df['high_high'].values == True
    with np.errstate(divide='ignore', invalid='ignore'):
        df['base'] = ((df['rally'].shift().values == True) | (df['rally2'].shift().values == True)) \
                  & ((abs(df['open_close'].values) / abs(df['open_close'].shift().values)) < basing_percentage) \
                  & (df['open_close'].values < 0)
    df['rbr'] = (df['rally2'].values == True) \
        & (df['base'].shift().values == True) \
        & (df['rally'].shift(periods=2).values == True)
    df['rbr2'] = (df['rbr'].values == True) \
        | (df['rbr'].shift(periods=-1).values == True) \
        | (df['rbr'].shift(periods=-2).values == True)
    df['Symbol'] = x
    df['Count'] = 1
    df2 = df2.append(df)

df2 = df2.drop(columns=['rbr'])
df2 = df2.rename(columns={'rbr2': 'rbr'})
df_rbr = df2[df2['rbr'] != False]

rbr_count = df_rbr.groupby(['Symbol', 'date'])['Count'].count().reset_index()
rbr_count['Count'] = np.ceil(rbr_count['Count']/3)
min_date = datetime.strptime(rbr_count['date'].min(), '%m/%d/%Y')
max_date = datetime.strptime(rbr_count['date'].max(), '%m/%d/%Y')

days = (max_date - min_date).days
rbr_count.to_csv('dist/rbr_count' + '.csv')
