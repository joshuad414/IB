from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

stock = Stock('AAPL', 'SMART', 'USD')

#order = MarketOrder('BUY', 2)
#trade = ib.placeOrder(stock, order)


executed_trades = ib.reqExecutions()
for i in range(0, len(executed_trades)):
    print(i+1, executed_trades[i][0].symbol, executed_trades[i][1].price, executed_trades[i][1].cumQty, executed_trades[i][1].side)

#ib.run()
