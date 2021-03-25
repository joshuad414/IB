from ib_insync import *
import time
from Requirements import stock

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=3)

# equities
spy = 'SPY'
qqq = 'QQQ'
aapl = 'AAPL'
rally_percentage = 0.0008
basing_percentage = 0.9

# stock = aapl
x = stock

stock = Stock(stock, 'SMART', 'USD')
bar_time_frame = '5 mins'
rt_hours = True

bar = ib.reqHistoricalData(stock, endDateTime='', durationStr='1 D', barSizeSetting=bar_time_frame,
                           whatToShow='MIDPOINT', useRTH=rt_hours, keepUpToDate=True)


def on_bar_update(bars: BarDataList, has_new_bar: bool):
    if has_new_bar:
        df2 = util.df(bars)
        update_rbr_data(df2)


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
    df['Symbol'] = x
    df['basing_percent'] = df['open'].values / df['open'].shift().values
    #df = df.drop(columns=['open_close', 'open_high', 'high1', 'high2', 'high_high', 'base', 'rally', 'rally2', 'rbr'])
    df = df.drop(columns=['rbr'])
    df = df.rename(columns={'rbr2': 'rbr'})
    df.to_csv('historical_data.csv')
    df_rbr = df[df['rbr'] != False]
    df_rbr.to_csv('rbr.csv')


# option data
strike_price = 121
option_month = str(time.localtime().tm_mon)
option_year = str(time.localtime().tm_year)
if len(option_month) == 1:
    option_month = '0' + option_month
option_contract = Option(aapl, '20210401', strike_price, 'C', 'SMART', '100', 'USD')

# Stock Ticker Data
market_data = ib.reqMktData(stock, '', False, False)


def on_pending_ticker(ticker):
    df = util.df(bar)
    #update_rbr_data(df)
    open_candle = df['open'][len(df) - 2]
    time_candle = df['date'][len(df) - 2]
    last_price = market_data.last
    print(x, 'Last Price:', last_price, open_candle)
    # if last_price >= 121.25:
    #     mark_order = MarketOrder('BUY', 1)
    #     trade = ib.placeOrder(option_contract, mark_order)
    #     ib.disconnect()
    #     print('Order Filled')


ib.barUpdateEvent += on_bar_update
ib.pendingTickersEvent += on_pending_ticker
ib.run()
