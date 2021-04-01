from ib_insync import *
import datetime
import pandas as pd

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=12)

executed_trades = ib.reqExecutions()

df2 = pd.DataFrame()


# print(df)
for i in range(3, len(executed_trades)):
    df = pd.DataFrame()
    symbol = executed_trades[i][0].symbol
    price = executed_trades[i][1].price
    amount = executed_trades[i][1].cumQty
    trade = executed_trades[i][1].side
    time_trade = executed_trades[i][3]
    trade_id = executed_trades[i][1].permId
    print(i+1, symbol, price, amount, trade, trade_id)
    df['Symbol'] = symbol
    df['Price'] = price
    df['Amount'] = amount
    df['Trade'] = trade
    df2 = df2.append(df)

last_trade = executed_trades[-1][1].permId
trade_type = executed_trades[-1][1].side
print(last_trade, trade_type)



x = executed_trades[0][3]
y = datetime.datetime.now(tz=datetime.timezone.utc)


'''
count = 0
for i in range(0, len(executed_trades)):
    if executed_trades[i][1].side == 'SLD':
        count += 1
        print(i, executed_trades[i][3])
'''
