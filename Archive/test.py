import time
import pandas as pd
from pandas import DataFrame

df: DataFrame = pd.DataFrame(columns=['stock','shares bought',' avg price', 'shares sold', 'total shares sold'])

shares_bought = 100
shares_sold = shares_bought * 0.2
shares = 0
stock = 'AAPl'
executed_trade_price = 139.00
total_shares_sold = 0
total_shares_remain = shares_bought
time_threshold = 1000000000000000000#0.05

i = 1
t0 = time.time()

if (i<1000):
    while (i > 0) & (i<3):
        t1 = time.time()
        total_time = t1 -t0
        #df.loc[len(df.index)] = ['',total_time, i]
        #print(total_time)
        if (total_time > time_threshold):
            total_shares_remain = 0
            print('Sold', shares_bought - total_shares_sold,'remaining shares, time exceeded')
            break
        elif (i == 1):
            total_shares_sold = shares_sold
            total_shares_remain = shares_bought - total_shares_sold
            print('1 Trade Executed Sold', shares_sold, "shares of", stock, "@", executed_trade_price)
            print('')
            df.loc[len(df.index)] = ['AAPL', shares_bought, 137.00, shares_sold, shares_bought-shares]
            break
        elif (i == 2):
            total_shares_sold = shares_sold * 2
            total_shares_remain = shares_bought - total_shares_sold
            print('2 Trade Executed Sold', shares_sold, "shares of", stock, "@", executed_trade_price)
            print('')
            df.loc[len(df.index)] = ['AAPL', shares_bought, 137.00, shares_sold, shares_bought-shares]
        elif (i == 3):
            total_shares_sold = shares_sold * 3
            total_shares_remain = shares_bought - total_shares_sold
            print('3 Trade Executed Sold', shares_sold, "shares of", stock, "@", executed_trade_price)
            print('')
            df.loc[len(df.index)] = ['AAPL', shares_bought, 137.00, shares_sold, shares_bought-shares]
        elif (i == 4):
            total_shares_sold = shares_sold * 4
            total_shares_remain = shares_bought - total_shares_sold
            print('4 Trade Executed Sold', shares_sold, "shares of", stock, "@", executed_trade_price)
            print('')
            df.loc[len(df.index)] = ['AAPL', shares_bought, 137.00, shares_sold, shares_bought-shares]
        elif (i == 5):
            total_shares_sold = shares_sold * 5
            total_shares_remain = shares_bought - total_shares_sold
            print('5 Trade Executed Sold', shares_sold, "shares of", stock, "@", executed_trade_price)
            print('')
            df.loc[len(df.index)] = ['AAPL', shares_bought, 137.00, shares_sold, shares_bought-shares]
            break
        i += 1
    print('break')
    if (total_shares_remain != 0):
        print('Stop Loss', total_shares_remain, "shares of", stock, "sold @", executed_trade_price)


t3 = time.time()
total = t3-t0
#print(total)
#df.to_csv('executed_trades.csv')