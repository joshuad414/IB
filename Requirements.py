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
nflx = 'NFLX'

stock = spy
symbol = stock


# RBR Single/All
rally_percentage = 0.0007
basing_percentage = 0.9
bar_time_frame = '5 mins'
rt_hours = True


# RBR History
bar_time_frame_historic = '5 mins'
duration = '1 D'


# Option Data
option_day = '09'
option_month = str(time.localtime().tm_mon)
option_year = str(time.localtime().tm_year)
if len(option_month) < 10:
    option_month = '0'+option_month
option_date = option_year + option_month + option_day
strike_price = 407


# Buying/Selling
qty_buy = 5
qty_sold = qty_buy * (1/5)
time_threshold = 240
sell_1_price = 1.025
sell_2_price = 1.05
sell_3_price = 1.1
sell_4_price = 1.15
sell_5_price = 1.2


# Stock List for RBR All
stock_list = [spy, qqq, aapl, msft, nio, amd, nvda, ba, cciv, baba, nke, dis, fb, oxy, twtr, tsla, nflx]
