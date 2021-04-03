from ib_insync import *
import datetime
import pandas as pd

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=12)

executed_trades = ib.reqExecutions()

df_executed_trades = pd.DataFrame()

list_1 = []
list_2 = []


for i in range(0, len(executed_trades)):
    symbol = executed_trades[i][0].symbol
    price = executed_trades[i][1].price
    amount = executed_trades[i][1].cumQty
    trade = executed_trades[i][1].side
    time_trade = executed_trades[i][3]
    trade_id = executed_trades[i][1].permId
    list_1.append(symbol)
    list_1.append(price)
    list_1.append(amount)
    list_1.append(trade)
    list_1.append(trade_id)
    list_1.append(time_trade)
    list_2.append(list_1)
    list_1 = []


df_executed_trades = pd.DataFrame(list_2, columns=['Symbol', 'Price', 'Amount', 'Trade', 'Trade ID', 'Time'])

df_executed_trades = df_executed_trades[df_executed_trades['Symbol'] == 'MSFT']
df_executed_trades = df_executed_trades[df_executed_trades['Trade'] == 'BOT']
# df_executed_trades = df_executed_trades.iloc[[-1]]
trade_price = df_executed_trades['Price'].values[-1]
print(trade_price)

df_executed_trades.to_csv('Executed_Trades/data.csv')
