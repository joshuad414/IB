from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=10)

# stock = Stock('AAPL', 'SMART', 'USD')
# order = MarketOrder('BUY', 2)
# trade = ib.placeOrder(stock, order)

option_contract = Option('MSFT', '20210409', 240, 'C', 'SMART', '100', 'USD')
option_data = ib.reqMktData(option_contract, '', False, False)

ib.placeOrder(option_contract, MarketOrder('BUY', 1))

print(option_data.last, option_data.marketPrice(), option_data.bid, option_data.ask)

ib.run()
