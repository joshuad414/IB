from ib_insync import *
import numpy as np
import pandas as pd
from Requirements import symbol, basing_percentage, rally_percentage, option_date, strike_price, qty_buy, qty_sold, sell_1_price, sell_2_price, sell_3_price, sell_4_price, sell_5_price

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)


stock = Stock(symbol, 'SMART', 'USD')
market_data = ib.reqMktData(stock, '', False, False)
option_contract = Option(symbol, option_date, strike_price, 'C', 'SMART', '100', 'USD')
option_data = ib.reqMktData(option_contract, '', False, False)
bar = ib.reqHistoricalData(stock, endDateTime='', durationStr='1 D', barSizeSetting='5 mins',
                           whatToShow='MIDPOINT', useRTH=True, keepUpToDate=True)


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
    df = df.drop(columns=['open_close', 'open_high', 'high1', 'high2', 'high_high', 'base', 'rally', 'rally2', 'rbr'])
    df = df.rename(columns={'rbr2': 'rbr'})


count = 0
trades = 0
executed_buy_price = 0
executed_trade_price = 0
exec_trade_list = []
last_price_list = []
qty_buy_list = []
qty_sell_list = []


def on_pending_ticker(ticker):
    global count, trades, executed_buy_price, executed_trade_price, exec_trade_list, last_price_list, qty_buy_list, qty_sell_list

    df = util.df(bar)
    update_rbr_data(df)
    base_high = df['high'].values[-2]                      # high value from basing candle
    watching = df['onWatch'].values[-2]                    # boolean from onWatch column for the last closed candle
    basing_open = df['open'].values[-2]                    # pulls boolean from base column for the last closed candle
    last_price_stock = market_data.last                    # get last ticker price
    day_value = last_price_stock - df['open'].values[0]    # check if stock is positive or negative for the day
    last_price_option = option_data.last
    # strike_price = np.floor(base_high)                   # gets strike price using the floor of the basing candle

    # Buy x (5/5)
    if last_price_stock > base_high and watching == True and count == 0 and trades == 0:
        ib.placeOrder(option_contract, MarketOrder('BUY', qty_buy))
        count += qty_buy
        executed_buy_price = option_data.last
        exec_trade_list.append(executed_buy_price)
        last_price_list.append(last_price_stock)
        qty_buy_list.append(qty_buy)

    # Sell x/5 (1/5)
    elif ((executed_buy_price * sell_1_price) > last_price_option) and count != 0 and trades != 1:
        ib.placeOrder(option_contract, MarketOrder('SELL', qty_sold))
        count -= qty_sold
        trades = 1
        executed_trade_price = option_data.last
        exec_trade_list.append(executed_trade_price)
        last_price_list.append(last_price_stock)
        qty_sell_list.append(qty_sold)

    # Sell x/5 (2/5)
    elif ((executed_buy_price * sell_2_price) > last_price_option) and count != 0 and trades != 2:
        ib.placeOrder(option_contract, MarketOrder('SELL', qty_sold))
        count -= qty_sold
        trades = 2
        executed_trade_price = option_data.last
        exec_trade_list.append(executed_trade_price)
        last_price_list.append(last_price_stock)
        qty_sell_list.append(qty_sold)

    # Sell x/5 (3/5)
    elif ((executed_buy_price * sell_3_price) > last_price_option) and count != 0 and trades != 3:
        ib.placeOrder(option_contract, MarketOrder('SELL', qty_sold))
        count -= qty_sold
        trades = 3
        executed_trade_price = option_data.last
        exec_trade_list.append(executed_trade_price)
        last_price_list.append(last_price_stock)
        qty_sell_list.append(qty_sold)

    # Sell x/5 (4/5)
    elif ((executed_buy_price * sell_4_price) > last_price_option) and count != 0 and trades != 4:
        ib.placeOrder(option_contract, MarketOrder('SELL', qty_sold))
        count -= qty_sold
        trades = 4
        executed_trade_price = option_data.last
        exec_trade_list.append(executed_trade_price)
        last_price_list.append(last_price_stock)
        qty_sell_list.append(qty_sold)

    # Sell x/5 (5/5)
    elif ((executed_buy_price * sell_5_price) > last_price_option) and count != 0 and trades != 5:
        ib.placeOrder(option_contract, MarketOrder('SELL', qty_sold))
        count -= qty_sold
        trades = 5
        executed_trade_price = option_data.last
        exec_trade_list.append(executed_trade_price)
        last_price_list.append(last_price_stock)
        qty_sell_list.append(qty_sold)
        trade_data = pd.DataFrame({'Executed Trade Price': exec_trade_list, 'Stock Price': last_price_list,
                                   'Qty Buy': qty_buy_list, 'Qty Sold': qty_sell_list})
        trade_data.to_csv('trade_data.csv')

    # Sell remaining
    elif last_price_stock < basing_open and count != 0:
        ib.placeOrder(option_contract, MarketOrder('SELL', count))
        count = 0
        trades = 0
        exec_trade_list.append(executed_trade_price)
        last_price_list.append(last_price_stock)
        qty_sell_list.append(qty_sold)
        trade_data = pd.DataFrame({'Executed Trade Price':exec_trade_list, 'Stock Price':last_price_list,
                                  'Qty Buy': qty_buy_list, 'Qty Sold': qty_sell_list})
        trade_data.to_csv('trade_data.csv')

    else:
        print(symbol, 'Last Price:', last_price_stock, last_price_option, '   Basing Candle High:',
              base_high, '  Open:', basing_open, '    Watching: ', watching, '   Executed Trade Price: ', executed_trade_price, '   Trades: ', trades, '   Count: ', count)


ib.barUpdateEvent += on_bar_update
ib.pendingTickersEvent += on_pending_ticker
ib.run()
