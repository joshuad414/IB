from ib_insync import *
import numpy as np
import pandas as pd
import time
import datetime

qty_buy = 0
qty_sold = 0


class Equities:
    def __init__(self):
        self.spy = 'SPY'
        self.qqq = 'QQQ'
        self.aapl = 'AAPL'
        self.msft = 'MSFT'
        self.nio = 'NIO'
        self.amd = 'AMD'
        self.nvda = 'NVDA'
        self.ba = 'BA'
        self.cciv = 'CCIV'
        self.baba = 'BABA'
        self.nke = 'NKE'
        self.dis = 'DIS'
        self.fb = 'FB'
        self.oxy = 'OXY'
        self.twtr = 'TWTR'
        self.tsla = 'TSLA'
        self.nflx = 'NFLX'

    def stock_list(self):
        stock_list = [self.spy, self.qqq, self.aapl, self.msft, self.nio, self.amd, self.nvda, self.ba, self.cciv,
                      self.baba, self.nke, self.dis, self.fb, self.oxy, self.twtr, self.tsla, self.nflx]
        return stock_list


class RBR:
    def __init__(self, symbol, option_date, strike_price, total_investment, trading, ibid):
        self.symbol = symbol
        self.option_date = option_date
        self.strike_price = strike_price
        self.trading = trading
        self.ibid = ibid
        self.total_investment = total_investment
        self.bar_time_frame = '5 mins'
        self.rt_hours = True
        self.rally_percentage = 0.0007
        self.basing_percentage = 0.9
        self.time_threshold = 240
        self.sell_1_price = 1.025
        self.sell_2_price = 1.05
        self.sell_3_price = 1.1
        self.sell_4_price = 1.15
        self.sell_5_price = 1.2
        self.trade_price = 0
        self.count = 0
        self.trades = 0
        self.executed_buy_price = 0
        self.exec_trade_list = []
        self.last_price_list = []
        self.qty_list = []
        self.basing_open_list = []
        self.basing_high_list = []
        self.time_list = []
        self.t0 = 0
        self.t1 = 0

        self.ib = IB()
        self.ib.connect('127.0.0.1', 7497, clientId=self.ibid)
        self.positions = self.ib.positions()

        if self.trading:
            self.bar = self.ib.reqHistoricalData(self.stock_info(), endDateTime='', durationStr='1 D',
                                                 barSizeSetting=self.bar_time_frame, whatToShow='MIDPOINT',
                                                 useRTH=self.rt_hours, keepUpToDate=True)
            self.stock_ticker = self.ib.reqMktData(self.stock_info(), '', False, False)
            self.option_ticker = self.ib.reqMktData(self.option_info(), '', False, False)
        self.ib.pendingTickersEvent += self.on_pending_ticker
        self.ib.barUpdateEvent += self.on_bar_update

    def stock_info(self):
        x = Stock(self.symbol, 'SMART', 'USD')
        return x

    def option_info(self):
        y = Option(self.symbol, self.option_date, self.strike_price, 'C', 'SMART', '100', 'USD')
        return y

    def rbr_all(self):
        stock_list = Equities().stock_list()
        df2 = pd.DataFrame()

        for x in stock_list:
            stock = Stock(x, 'SMART', 'USD')
            bars = self.ib.reqHistoricalData(stock, endDateTime='', durationStr='1 D',
                                             barSizeSetting=self.bar_time_frame, whatToShow='MIDPOINT',
                                             useRTH=self.rt_hours, keepUpToDate=True)
            df = util.df(bars)
            df.drop(['volume', 'average', 'barCount'], axis=1, inplace=True)
            df['date'] = df['date'].dt.strftime('%H:%M')
            df['open_close'] = (df['close'].values - df['open'].values) / df['open'].values
            df['open_high'] = (df['high'].values - df['open'].values) / df['open'].values
            df['high1'] = df['high'].shift().values
            df['high2'] = df['high'].shift(periods=2).values
            df['high_high'] = (df['high'].values > df['high1'].values) & (df['high'].values > df['high2'].values)
            df['rally'] = df['open_close'].values > self.rally_percentage
            df['rally2'] = df['high_high'].values == True
            with np.errstate(divide='ignore', invalid='ignore'):
                df['base'] = ((df['rally'].shift().values == True) | (df['rally2'].shift().values == True)) \
                             & ((abs(df['open_close'].values) / abs(df['open_close'].shift().values))
                                < self.basing_percentage) & (df['open_close'].values < 0)
            df['rbr'] = (df['rally2'].values == True) \
                        & (df['base'].shift().values == True) \
                        & (df['rally'].shift(periods=2).values == True)
            df['rbr2'] = (df['rbr'].values == True) \
                         | (df['rbr'].shift(periods=-1).values == True) \
                         | (df['rbr'].shift(periods=-2).values == True)
            with np.errstate(divide='ignore', invalid='ignore'):
                df['onWatch'] = (df['open_close'].values < 0) & (df['rally'].shift().values == True) \
                                & ((abs(df['open_close'].values) / abs(df['open_close'].shift().values))
                                   < self.basing_percentage)
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
            df['bar'] = (df['bar1'].values + df['bar2'].values + df['bar3'].values + df['bar4'].values + df[
                'bar5'].values)
            with np.errstate(divide='ignore', invalid='ignore'):
                df['basing_percent'] = abs(df['open_close'].values) / abs(df['open_close'].shift().values)
            df2 = df2.append(df)

        df2 = df2.drop(columns=['rbr'])
        df2 = df2.rename(columns={'rbr2': 'rbr'})
        df2.to_csv('dist/historical_data.csv')
        df_rbr = df2[df2['rbr'] != False]
        df_rbr.to_csv('dist/rbr.csv')
        print('Done!')

    def update_rbr_data(self, df_rbr):
        df_rbr.drop(['volume', 'average', 'barCount'], axis=1, inplace=True)
        df_rbr['date'] = df_rbr['date'].dt.strftime('%H:%M')
        df_rbr['open_close'] = (df_rbr['close'].values - df_rbr['open'].values) / df_rbr['open'].values
        df_rbr['open_high'] = (df_rbr['high'].values - df_rbr['open'].values) / df_rbr['open'].values
        df_rbr['high1'] = df_rbr['high'].shift().values
        df_rbr['high2'] = df_rbr['high'].shift(periods=2).values
        df_rbr['high_high'] = (df_rbr['high'].values > df_rbr['high1'].values) & (df_rbr['high'].values >
                                                                                  df_rbr['high2'].values)
        df_rbr['rally'] = df_rbr['open_close'].values > self.rally_percentage
        df_rbr['rally2'] = df_rbr['high_high'].values == True
        with np.errstate(divide='ignore', invalid='ignore'):
            df_rbr['base'] = ((df_rbr['rally'].shift().values == True) | (df_rbr['rally2'].shift().values == True)) \
                             & ((abs(df_rbr['open_close'].values) / abs(df_rbr['open_close'].shift().values))
                                < self.basing_percentage) \
                             & (df_rbr['open_close'].values < 0)
        df_rbr['rbr'] = (df_rbr['rally2'].values == True) & (df_rbr['base'].shift().values == True) \
            & (df_rbr['rally'].shift(periods=2).values == True)
        df_rbr['rbr2'] = (df_rbr['rbr'].values == True) | (df_rbr['rbr'].shift(periods=-1).values == True) \
            | (df_rbr['rbr'].shift(periods=-2).values == True)
        with np.errstate(divide='ignore', invalid='ignore'):
            df_rbr['onWatch'] = (df_rbr['open_close'].values < 0) \
                                & (df_rbr['rally'].shift().values == True) \
                                & ((abs(df_rbr['open_close'].values) / abs(df_rbr['open_close'].shift().values))
                                   < self.basing_percentage)
        df_rbr = df_rbr.drop(
            columns=['open_close', 'open_high', 'high1', 'high2', 'high_high', 'base', 'rally', 'rally2', 'rbr'])
        df_rbr = df_rbr.rename(columns={'rbr2': 'rbr'})
        return df_rbr

    def on_bar_update(self, bars: BarDataList, has_new_bar: bool):
        if has_new_bar:
            df = util.df(bars)

    def get_executed_price(self):
        for i in range(0, len(self.positions)):
            stock = str(self.positions[i][1])
            stock = stock.split("symbol='", 1)[1]
            stock = stock.split("',", 1)[0]
            if self.symbol == stock:
                cost = self.positions[i][3]
                self.trade_price = np.round((cost-1) / 100, 2)
                break
            else:
                self.trade_price = 0
        return self.trade_price

    def option_buy_amount(self):
        last_price_option = self.option_ticker.last
        amount = np.floor(self.total_investment/(last_price_option*100))
        amount = 5 * np.round(amount/5)
        return amount

    def on_pending_ticker(self, ticker):
        global qty_buy, qty_sold
        df = util.df(self.bar)
        self.update_rbr_data(df)

        basing_high = df['high'].values[-2]         # high value from basing candle
        watching = df['onWatch'].values[-2]         # boolean from onWatch column for the last closed candle
        basing_open = df['open'].values[-2]         # pulls boolean from base column for the last closed candle
        last_price_stock = self.stock_ticker.last
        last_price_option = self.option_ticker.last

        if watching:
            qty_buy = self.option_buy_amount()
            qty_sold = qty_buy/5

            # Buy
            if last_price_stock > basing_high and watching and self.count == 0 and self.trades == 0 and \
                    ((self.t1 - self.t0) > 300 or (self.t1 - self.t0) == 0):
                self.ib.placeOrder(self.option_info(), MarketOrder('BUY', qty_buy))
                self.t0 = time.time()
                self.ib.sleep(5)
                self.count += qty_buy
                time_executed = datetime.datetime.now().strftime("%H:%M:%S")
                self.executed_buy_price = self.get_executed_price()

                self.exec_trade_list.append(self.executed_buy_price)
                self.last_price_list.append(last_price_stock)
                self.qty_list.append(qty_buy)
                self.basing_open_list.append(basing_open)
                self.basing_high_list.append(basing_high)
                self.time_list.append(time_executed)
                buy_data = pd.DataFrame({'Executed Trade Price': self.exec_trade_list,
                                         'Price of Stock': self.last_price_list, 'Qty': self.qty_list,
                                         'Basing Open': self.basing_open_list, 'Basing High': self.basing_high_list,
                                         'Time': self.time_list})
                buy_data.to_csv('Executed_Trades/trade_data_' + self.symbol + str(np.random.randint(1000)) + '.csv')
                print(self.symbol, self.count, 'BUY @', self.executed_buy_price, time_executed, self.trades)

            # Sell 1
            elif ((self.executed_buy_price * self.sell_1_price) < last_price_option) and self.count != 0 \
                    and self.trades == 0:
                self.ib.placeOrder(self.option_info(), MarketOrder('SELL', qty_sold))
                self.count -= qty_sold
                self.trades = 1
                executed_trade_price = self.option_ticker.last
                time_executed = datetime.datetime.now().strftime("%H:%M:%S")
                self.exec_trade_list.append(executed_trade_price)
                self.last_price_list.append(last_price_stock)
                self.qty_list.append(qty_sold)
                self.basing_open_list.append(basing_open)
                self.basing_high_list.append(basing_high)
                self.time_list.append(time_executed)
                print(qty_sold, 'SELL @', executed_trade_price, time_executed, self.trades)

            # Sell 2
            elif ((self.executed_buy_price * self.sell_2_price) < last_price_option) and self.count != 0 \
                    and self.trades == 1:
                self.ib.placeOrder(self.option_info(), MarketOrder('SELL', qty_sold))
                self.count -= qty_sold
                self.trades = 2
                executed_trade_price = self.option_ticker.last
                time_executed = datetime.datetime.now().strftime("%H:%M:%S")
                self.exec_trade_list.append(executed_trade_price)
                self.last_price_list.append(last_price_stock)
                self.qty_list.append(qty_sold)
                self.basing_open_list.append(basing_open)
                self.basing_high_list.append(basing_high)
                self.time_list.append(time_executed)
                print(qty_sold, 'SELL @', executed_trade_price, time_executed, self.trades)

            # Sell 3
            elif ((self.executed_buy_price * self.sell_3_price) < last_price_option) and self.count != 0 \
                    and self.trades == 2:
                self.ib.placeOrder(self.option_info(), MarketOrder('SELL', qty_sold))
                self.count -= qty_sold
                self.trades = 3
                executed_trade_price = self.option_ticker.last
                time_executed = datetime.datetime.now().strftime("%H:%M:%S")
                self.exec_trade_list.append(executed_trade_price)
                self.last_price_list.append(last_price_stock)
                self.qty_list.append(qty_sold)
                self.basing_open_list.append(basing_open)
                self.basing_high_list.append(basing_high)
                self.time_list.append(time_executed)
                print(qty_sold, 'SELL @', executed_trade_price, time_executed, self.trades)

            # Sell 4
            elif ((self.executed_buy_price * self.sell_4_price) < last_price_option) and self.count != 0 \
                    and self.trades == 3:
                self.ib.placeOrder(self.option_info(), MarketOrder('SELL', qty_sold))
                self.count -= qty_sold
                self.trades = 4
                executed_trade_price = self.option_ticker.last
                time_executed = datetime.datetime.now().strftime("%H:%M:%S")
                self.exec_trade_list.append(executed_trade_price)
                self.last_price_list.append(last_price_stock)
                self.qty_list.append(qty_sold)
                self.basing_open_list.append(basing_open)
                self.basing_high_list.append(basing_high)
                self.time_list.append(time_executed)
                print(qty_sold, 'SELL @', executed_trade_price, time_executed, self.trades)

            # Sell 5
            elif ((self.executed_buy_price * self.sell_5_price) > last_price_option) and self.count != 0 \
                    and self.trades == 4:
                self.ib.placeOrder(self.option_info(), MarketOrder('SELL', qty_sold))
                self.t1 = time.time()
                self.count -= qty_sold
                self.trades = 0
                executed_trade_price = self.option_ticker.last
                time_executed = datetime.datetime.now().strftime("%H:%M:%S")
                self.exec_trade_list.append(executed_trade_price)
                self.last_price_list.append(last_price_stock)
                self.qty_list.append(qty_sold)
                self.basing_open_list.append(basing_open)
                self.basing_high_list.append(basing_high)
                self.time_list.append(time_executed)
                trade_data = pd.DataFrame({'Executed Trade Price': self.exec_trade_list,
                                           'Price of Stock': self.last_price_list, 'Qty': self.qty_list,
                                           'Basing Open': self.basing_open_list, 'Basing High': self.basing_high_list,
                                           'Time': self.time_list})
                trade_data.to_csv('Executed_Trades/trade_data_' + self.symbol + str(np.random.randint(1000)) + '.csv')
                print(qty_sold, 'SELL @', executed_trade_price, time_executed, self.trades)

            # Sell remaining
            elif last_price_stock < basing_open and self.count != 0:
                self.ib.placeOrder(self.option_info(), MarketOrder('SELL', self.count))
                self.t1 = time.time()
                self.count = 0
                self.trades = 0
                executed_trade_price = self.option_ticker.last
                time_executed = datetime.datetime.now().strftime("%H:%M:%S")
                self.exec_trade_list.append(executed_trade_price)
                self.last_price_list.append(last_price_stock)
                self.qty_list.append(self.count)
                self.basing_open_list.append(basing_open)
                self.basing_high_list.append(basing_high)
                self.time_list.append(time_executed)
                trade_data = pd.DataFrame({'Executed Trade Price': self.exec_trade_list,
                                           'Price of Stock': self.last_price_list, 'Qty': self.qty_list,
                                           'Basing Open': self.basing_open_list, 'Basing High': self.basing_high_list,
                                           'Time': self.time_list})
                trade_data.to_csv('Executed_Trades/trade_data_' + self.symbol + str(np.random.randint(1000)) + '.csv')
                print(self.count, 'SELL @', executed_trade_price, time_executed, self.trades)
            
            print(self.symbol, ' Stock:', last_price_stock, '  Option:', last_price_option,
                  '  Basing High:', basing_high, '  Watching:', watching, '  Count:', self.count,
                  '  Trades:', self.trades, '  Executed Buy Price:', self.executed_buy_price)

    def run(self):
        self.ib.run()


def main(option_date, total_investment):
    """ Run: symbol, option date, strike price, investment amount, trading (boolean), IB ID """
    spy = RBR("SPY", option_date, 406, total_investment, True, 1)
    qqq = RBR("QQQ", option_date, 331, total_investment, True, 2)
    aapl = RBR("AAPL", option_date, 127, total_investment, True, 3)
    msft = RBR("MSFT", option_date, 250, total_investment, True, 4)
    nio = RBR("NIO", option_date, 40, total_investment, True, 5)
    dis = RBR("DIS", option_date, 190, total_investment, True, 6)
    nflx = RBR("NFLX", option_date, 545, total_investment, True, 7)
    nvda = RBR("NVDA", option_date, 555, total_investment, True, 8)
    fb = RBR("FB", option_date, 305, total_investment, True, 9)
    ba = RBR("BA", option_date, 255, total_investment, True, 10)

    spy.run()
    qqq.run()
    aapl.run()
    msft.run()
    nio.run()
    dis.run()
    nflx.run()
    nvda.run()
    fb.run()
    ba.run()


""" Option Date, Investment Amount """
main("20210409", 10000)
