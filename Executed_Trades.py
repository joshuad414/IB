from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=4)

executed_trades = ib.reqExecutions()
df = util.df(executed_trades)
#print(df)
for i in range(0, len(executed_trades)):
    print(i+1, executed_trades[i][0].symbol, executed_trades[i][1].price, executed_trades[i][1].cumQty, executed_trades[i][1].side)