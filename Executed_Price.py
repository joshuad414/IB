from ib_insync import *
import numpy as np


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=12)
positions = ib.positions()

trade_price = 0


def get_executed_price(symbol):
    global trade_price
    for i in range(0, len(positions)):
        stock = str(positions[i][1])
        stock = stock.split("symbol='", 1)[1]
        stock = stock.split("',", 1)[0]
        if symbol == stock:
            cost = positions[i][3]
            trade_price = np.round((cost-1)/100, 2)
            print(cost, trade_price)
            break
        else:
            trade_price = 0
    return trade_price


get_executed_price('SPY')
