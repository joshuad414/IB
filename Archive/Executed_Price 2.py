from ib_insync import *
import time

t0 = time.time()

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=12)

executed_trades = ib.reqExecutions()
positions = ib.reqPositions()

symbol = 'MSFT'
list_1 = []

for i in range(0, len(positions)):
    stock = str(positions[i][1])
    stock = stock.split("symbol='", 1)[1]
    stock = stock.split("',", 1)[0]
    size = positions[i][2]
    if size != 0 and symbol == stock:
        cost = positions[i][3]
        trade_price = cost/size/100
        list_1.append(stock)
        list_1.append(cost)
        list_1.append(trade_price)

print(list_1)
'''
list_1 = []
list_2 = []

for i in range(0, len(executed_trades)):
    symbol = executed_trades[i][0].symbol
    price = executed_trades[i][1].price
    trade = executed_trades[i][1].side
    if symbol == 'MSFT' and trade == 'BOT':
        list_1.append(price)
        list_2.append(list_1)
    list_1 = []

trade_price = list_2[-1]
'''


t1 = time.time()
print(t1-t0)
