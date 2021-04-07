from ib_insync import *
from Requirements import symbol, rally_percentage, basing_percentage, bar_time_frame, rt_hours

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=4)

stock = Stock(symbol, 'SMART', 'USD')
bar = ib.reqHistoricalData(stock, endDateTime='', durationStr='1 D', barSizeSetting=bar_time_frame,
                           whatToShow='MIDPOINT', useRTH=rt_hours, keepUpToDate=True)


def on_bar_update(bars: BarDataList, has_new_bar: bool):
    if has_new_bar:
        df = util.df(bars)


def update_rbr_data(df):
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
    df['Symbol'] = symbol
    df['basing_percent'] = df['open'].values / df['open'].shift().values
    df = df.drop(columns=['rbr'])
    df = df.rename(columns={'rbr2': 'rbr'})
    df.to_csv('historical_data.csv')
    df_rbr = df[df['rbr'] != False]
    df_rbr.to_csv('rbr.csv')


# Stock Ticker Data
market_data = ib.reqMktData(stock, '', False, False)


def on_pending_ticker(ticker):
    df = util.df(bar)
    update_rbr_data(df)
    open_candle = df['open'][len(df) - 2]
    last_price = market_data.last
    print(symbol, 'Last Price:', last_price, ' Basing Open:', open_candle)


ib.barUpdateEvent += on_bar_update
ib.pendingTickersEvent += on_pending_ticker
ib.run()
