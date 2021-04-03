from ib_insync import *
import time

t0 = time.time()
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=12)
positions = ib.positions()


def get_executed_price(symbol):
    for i in range(0, len(positions)):
        stock = str(positions[i][1])
        stock = stock.split("symbol='", 1)[1]
        stock = stock.split("',", 1)[0]
        size = positions[i][2]
        if size != 0 and symbol == stock:
            cost = positions[i][3]
            trade_price = cost/size/100
            break
        else:
            trade_price = 0
    return trade_price


s = get_executed_price('AAPL')
t1 = time.time()

print(s, (t1-t0))
