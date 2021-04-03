import RBR
from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=2)

s1 = RBR("MSFT")

bar = ib.reqHistoricalData(s1.stock_name(), endDateTime='', durationStr='1 D', barSizeSetting='5 mins',
                           whatToShow='MIDPOINT', useRTH=True, keepUpToDate=True)
df = util.df(bar)
s1.update_rbr_data(df)
