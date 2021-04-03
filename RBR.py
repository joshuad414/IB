from ib_insync import *
import pandas as pd
import numpy as np
import time


class RBR:
    def __init__(self, symbol):
        self.symbol = symbol

    def stock_info(self):
        x = Stock(self.symbol, 'SMART', 'USD')
        return x

    def rbr_data(self):
        rally_percentage = 0.0007
        basing_percentage = 0.9
        bar = ib.reqHistoricalData(self.stock_info(), endDateTime='', durationStr='1 D', barSizeSetting='5 mins',
                                   whatToShow='MIDPOINT', useRTH=True, keepUpToDate=True)
        df_rbr = util.df(bar)
        df_rbr.drop(['volume', 'average', 'barCount'], axis=1, inplace=True)
        df_rbr['date'] = df_rbr['date'].dt.strftime('%H:%M')
        df_rbr['open_close'] = (df_rbr['close'].values - df_rbr['open'].values) / df_rbr['open'].values
        df_rbr['open_high'] = (df_rbr['high'].values - df_rbr['open'].values) / df_rbr['open'].values
        df_rbr['high1'] = df_rbr['high'].shift().values
        df_rbr['high2'] = df_rbr['high'].shift(periods=2).values
        df_rbr['high_high'] = (df_rbr['high'].values > df_rbr['high1'].values) & (df_rbr['high'].values >
                                                                                  df_rbr['high2'].values)
        df_rbr['rally'] = df_rbr['open_close'].values > rally_percentage
        df_rbr['rally2'] = df_rbr['high_high'].values == True
        with np.errstate(divide='ignore'):
            df_rbr['base'] = ((df_rbr['rally'].shift().values == True) | (df_rbr['rally2'].shift().values == True)) \
                & ((abs(df_rbr['open_close'].values) / abs(df_rbr['open_close'].shift().values))
                   < basing_percentage) \
                & (df_rbr['open_close'].values < 0)
        df_rbr['rbr'] = (df_rbr['rally2'].values == True) \
            & (df_rbr['base'].shift().values == True) \
            & (df_rbr['rally'].shift(periods=2).values == True)
        df_rbr['rbr2'] = (df_rbr['rbr'].values == True) \
            | (df_rbr['rbr'].shift(periods=-1).values == True) \
            | (df_rbr['rbr'].shift(periods=-2).values == True)
        with np.errstate(divide='ignore'):
            df_rbr['onWatch'] = (df_rbr['open_close'].values < 0) \
                & (df_rbr['rally'].shift().values == True) \
                & ((abs(df_rbr['open_close'].values) / abs(df_rbr['open_close'].shift().values))
                   < basing_percentage)
        df_rbr = df_rbr.drop(
            columns=['open_close', 'open_high', 'high1', 'high2', 'high_high', 'base', 'rally', 'rally2', 'rbr'])
        df_rbr = df_rbr.rename(columns={'rbr2': 'rbr'})
        return df_rbr

    def get_executed_price(self):
        positions = ib.positions()
        for i in range(0, len(positions)):
            x = str(positions[i][1])
            x = x.split("symbol='", 1)[1]
            x = x.split("',", 1)[0]
            size = positions[i][2]
            if size != 0 and x == self.symbol:
                cost = positions[i][3]
                trade_price = (cost / size / 100)
                break
            else:
                trade_price = 0
        return trade_price

    def market_data(self):
        stock_data = ib.reqMktData(self.stock_info(), '', False, False)
        option_data = ib.reqMktData(self.stock_info(), '', False, False)

    '''Variables for Executing Order'''
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

    def on_pending_ticker(self, ticker):
        global count, trades, executed_buy_price, exec_trade_list, last_price_list, qty_list, \
            basing_open_list, basing_high_list, time_list, t1, t0

        df = self.rbr_data()
        base_high = df['high'].values[-2]  # high value from basing candle
        watching = df['onWatch'].values[-2]  # boolean from onWatch column for the last closed candle
        basing_open = df['open'].values[-2]  # pulls boolean from base column for the last closed candle
        last_price_stock = self.market_data().last  # get last ticker price
        last_price_option = option_data.last

        # Buy
        if last_price_stock > base_high and watching == True and count == 0 and trades == 0 and \
                ((t1 - t0) > 300 or (t1 - t0) == 0):
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
                                     'Qty': qty_list, 'Basing Open': basing_open_list,
                                     'Basing High': basing_high_list,
                                     'Time': time_list})
            buy_data.to_csv('Executed_Trades/trade_data_' + symbol + '.csv')
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
                                       'Qty': qty_list, 'Basing Open': basing_open_list,
                                       'Basing High': basing_high_list,
                                       'Time': time_list})
            trade_data.to_csv('Executed_Trades/trade_data_' + symbol + '.csv')
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
                                       'Qty': qty_list, 'Basing Open': basing_open_list,
                                       'Basing High': basing_high_list,
                                       'Time': time_list})
            trade_data.to_csv('Executed_Trades/trade_data_' + symbol + '.csv')
            print(count, 'SELL @', executed_trade_price, time_executed, trades)

'''Run'''
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

s1 = RBR("MSFT")

s1.get_executed_price()
s1.rbr_data()
