from ib_insync import *
import numpy as np
import pandas as pd
import datetime
import time
from Requirements import symbol, basing_percentage, rally_percentage, option_date, strike_price, qty_buy, qty_sold, \
    sell_1_price, sell_2_price, sell_3_price, sell_4_price, sell_5_price, bar_time_frame


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)

stock = Stock(symbol, 'SMART', 'USD')
market_data = ib.reqMktData(stock, '', False, False)
option_contract = Option(symbol, option_date, strike_price, 'C', 'SMART', '100', 'USD')
option_data = ib.reqMktData(option_contract, '', False, False)
bar = ib.reqHistoricalData(stock, endDateTime='', durationStr='1 D', barSizeSetting=bar_time_frame,
                           whatToShow='MIDPOINT', useRTH=True, keepUpToDate=True)
positions = ib.positions()


def get_executed_price(x):
    for i in range(0, len(positions)):
        a = str(positions[i][1])
        a = a.split("symbol='", 1)[1]
        a = a.split("',", 1)[0]
        if x == a:
            cost = positions[i][3]
            trade_price = np.round((cost-1)/100, 2)
            break
        else:
            trade_price = 0
    return trade_price


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
exec_trade_list = []
last_price_list = []
qty_list = []
basing_open_list = []
basing_high_list = []
time_list = []
t0 = 0
t1 = 0


def on_pending_ticker(ticker):
    global count, trades, executed_buy_price, exec_trade_list, last_price_list, qty_list, \
        basing_open_list, basing_high_list, time_list, t1, t0

    df = util.df(bar)
    update_rbr_data(df)
    base_high = df['high'].values[-2]  # high value from basing candle
    watching = df['onWatch'].values[-2]  # boolean from onWatch column for the last closed candle
    basing_open = df['open'].values[-2]  # pulls boolean from base column for the last closed candle
    last_price_stock = market_data.last  # get last ticker price
    last_price_option = option_data.last

    # Buy
    if last_price_stock > base_high and watching == True and count == 0 and trades == 0 and \
            ((t1-t0) > 300 or (t1-t0) == 0):
        ib.placeOrder(option_contract, MarketOrder('BUY', qty_buy))
        t0 = time.time()
        ib.sleep(3)
        count += qty_buy
        time_executed = datetime.datetime.now().strftime("%H:%M:%S")
        executed_buy_price = get_executed_price(symbol)
        exec_trade_list.append(executed_buy_price)
        last_price_list.append(last_price_stock)
        qty_list.append(qty_buy)
        basing_open_list.append(basing_open)
        basing_high_list.append(base_high)
        time_list.append(time_executed)
        buy_data = pd.DataFrame({'Executed Trade Price': exec_trade_list, 'Price of Stock': last_price_list,
                                 'Qty': qty_list, 'Basing Open': basing_open_list, 'Basing High': basing_high_list,
                                 'Time': time_list})
        buy_data.to_csv('Executed_Trades/trade_data_'+symbol+'.csv')
        print(buy_data)
        print(count, 'BUY @', executed_buy_price, time_executed, trades)

    # Sell 1
    elif ((executed_buy_price * sell_1_price) < last_price_option) and count != 0 and trades == 0:
        ib.placeOrder(option_contract, MarketOrder('SELL', qty_sold))
        count -= qty_sold
        trades = 1
        executed_trade_price = option_data.last
        time_executed = datetime.datetime.now().strftime("%H:%M:%S")
        exec_trade_list.append(executed_trade_price)
        last_price_list.append(last_price_stock)
        qty_list.append(qty_sold)
        basing_open_list.append(basing_open)
        basing_high_list.append(base_high)
        time_list.append(time_executed)
        print(qty_sold, 'SELL @', executed_trade_price, time_executed, trades)

    # Sell 2
    elif ((executed_buy_price * sell_2_price) < last_price_option) and count != 0 and trades == 1:
        ib.placeOrder(option_contract, MarketOrder('SELL', qty_sold))
        count -= qty_sold
        trades = 2
        executed_trade_price = option_data.last
        time_executed = datetime.datetime.now().strftime("%H:%M:%S")
        exec_trade_list.append(executed_trade_price)
        last_price_list.append(last_price_stock)
        qty_list.append(qty_sold)
        basing_open_list.append(basing_open)
        basing_high_list.append(base_high)
        time_list.append(time_executed)
        print(qty_sold, 'SELL @', executed_trade_price, time_executed, trades)

    # Sell 3
    elif ((executed_buy_price * sell_3_price) < last_price_option) and count != 0 and trades == 2:
        ib.placeOrder(option_contract, MarketOrder('SELL', qty_sold))
        count -= qty_sold
        trades = 3
        executed_trade_price = option_data.last
        time_executed = datetime.datetime.now().strftime("%H:%M:%S")
        exec_trade_list.append(executed_trade_price)
        last_price_list.append(last_price_stock)
        qty_list.append(qty_sold)
        basing_open_list.append(basing_open)
        basing_high_list.append(base_high)
        time_list.append(time_executed)
        print(qty_sold, 'SELL @', executed_trade_price, time_executed, trades)

    # Sell 4
    elif ((executed_buy_price * sell_4_price) < last_price_option) and count != 0 and trades == 3:
        ib.placeOrder(option_contract, MarketOrder('SELL', qty_sold))
        count -= qty_sold
        trades = 4
        executed_trade_price = option_data.last
        time_executed = datetime.datetime.now().strftime("%H:%M:%S")
        exec_trade_list.append(executed_trade_price)
        last_price_list.append(last_price_stock)
        qty_list.append(qty_sold)
        basing_open_list.append(basing_open)
        basing_high_list.append(base_high)
        time_list.append(time_executed)
        print(qty_sold, 'SELL @', executed_trade_price, time_executed)

    # Sell 5
    elif ((executed_buy_price * sell_5_price) > last_price_option) and count != 0 and trades == 4:
        ib.placeOrder(option_contract, MarketOrder('SELL', qty_sold))
        t1 = time.time()
        count -= qty_sold
        trades = 0
        executed_trade_price = option_data.last
        time_executed = datetime.datetime.now().strftime("%H:%M:%S")
        exec_trade_list.append(executed_trade_price)
        last_price_list.append(last_price_stock)
        qty_list.append(qty_sold)
        basing_open_list.append(basing_open)
        basing_high_list.append(base_high)
        time_list.append(time_executed)
        trade_data = pd.DataFrame({'Executed Trade Price': exec_trade_list, 'Price of Stock': last_price_list,
                                   'Qty': qty_list, 'Basing Open': basing_open_list, 'Basing High': basing_high_list,
                                   'Time': time_list})
        trade_data.to_csv('Executed_Trades/trade_data_'+symbol+'.csv')
        print(qty_sold, 'SELL @', executed_trade_price, time_executed, trades)

    # Sell remaining
    elif last_price_stock < basing_open and count != 0:
        ib.placeOrder(option_contract, MarketOrder('SELL', count))
        t1 = time.time()
        count = 0
        trades = 0
        executed_trade_price = option_data.last
        time_executed = datetime.datetime.now().strftime("%H:%M:%S")
        exec_trade_list.append(executed_trade_price)
        last_price_list.append(last_price_stock)
        qty_list.append(count)
        basing_open_list.append(basing_open)
        basing_high_list.append(base_high)
        time_list.append(time_executed)
        trade_data = pd.DataFrame({'Executed Trade Price': exec_trade_list, 'Price of Stock': last_price_list,
                                   'Qty': qty_list, 'Basing Open': basing_open_list, 'Basing High': basing_high_list,
                                   'Time': time_list})
        trade_data.to_csv('Executed_Trades/trade_data_'+symbol+'.csv')
        print(count, 'SELL @', executed_trade_price, time_executed, trades)


ib.barUpdateEvent += on_bar_update
ib.pendingTickersEvent += on_pending_ticker
ib.run()
