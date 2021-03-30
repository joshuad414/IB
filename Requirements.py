'''
libraries:
ibsync
streamlit
altair
pandas
numpy
time
datetime
'''


import time


# Equities
spy = 'SPY'
qqq = 'QQQ'
aapl = 'AAPL'
msft = 'MSFT'
nio = 'NIO'
amd = 'AMD'
nvda = 'NVDA'
ba = 'BA'
cciv = 'CCIV'
baba = 'BABA'
nke = 'NKE'
dis = 'DIS'
fb = 'FB'
oxy = 'OXY'
twtr = 'TWTR'
tsla = 'TSLA'


# RBR Single
rally_percentage = 0.0007
basing_percentage = 0.9
stock = aapl
symbol = stock
bar_time_frame = '5 mins'
rt_hours = True


# RBR History
bar_time_frame_historic = '5 mins'
duration = '10 D'


# Option Data
option_month = str(time.localtime().tm_mon)
option_year = str(time.localtime().tm_year)
if len(option_month) == 1:
    option_month = '0'+option_month
option_date = option_year + option_month
strike_price = 121


# Stock List for RBR All
stock_list = [spy, qqq, aapl, msft, nio, amd, nvda, ba, cciv, baba, nke, dis, fb, oxy, twtr, tsla]
