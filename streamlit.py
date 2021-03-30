# streamlit run streamlit.py
import streamlit as st
import pandas as pd
import altair as alt
import time
from Requirements import rally_percentage, basing_percentage, bar_time_frame
from datetime import datetime
import numpy as np



st.sidebar.title("Interactive Brokers Trading Automation")
option = st.sidebar.selectbox("Which Dashboard?",('Rally Base Rally', 'Rally Base Rally All', 'Historical RBR','Executed Orders', 'Watch List'), 0)

if option == 'Rally Base Rally':
    rally_percentage = st.sidebar.markdown("Minimum Percentage for Candle to be considered a **Rally: "+str(rally_percentage)+"**")
    st.sidebar.markdown("(open_close Column)")
    st.sidebar.markdown("")
    st.sidebar.markdown("Maximum Percentage of Basing candle drop to Rally candle Rise: **"+str(basing_percentage)+"**")
    st.sidebar.markdown("the larger the percentage the larger the red basing candle")
    st.sidebar.markdown("(basing_percent Column)")

    st.title("Rally Base Rally")
    df = pd.read_csv('historical_data.csv')
    symbol = df['Symbol'][0]
    last_time = df['date'].values[-1]
    watch_list = df[(df['onWatch'] == 1) & (df['date'] >= last_time)]
    watch_list = watch_list[['Symbol','date','open','high','low']]
    df_rbr = pd.read_csv('rbr.csv')
    df = df[['date','open','high','low','close','open_close','basing_percent','onWatch','rally','base','rbr','Symbol']]
    df_rbr = df_rbr[['date','open','high','low','close','onWatch']]

    def highlight_basing(x):
        if x['onWatch'] == 1:
            return ['background-color: lightyellow'] * len(df_rbr.columns)
        else:
            return ['background-color: white'] * (len(df_rbr.columns))

    def highlight_rbr(x):
        if x['rbr'] == 1:
            return ['background-color: lightgreen'] * len(df.columns)
        elif x['onWatch'] == 1:
            return ['background-color: lightyellow'] * len(df.columns)
        else:
            return ['background-color: white'] * (len(df.columns))


    st.subheader('Historical '+bar_time_frame+' for '+symbol)
    st.dataframe(df.style.apply(highlight_rbr, axis=1))

    st.subheader(symbol+' RBR')
    st.dataframe(df_rbr.style.apply(highlight_basing, axis=1))
    x = str(int((len(df_rbr)/3)))
    st.write(x+' Total RBR for '+symbol)

    st.subheader(symbol+' 5 min Chart')
    st.write("https://www.barchart.com/stocks/quotes/"+symbol+"/interactive-chart")
    df['open_day'] = df['open'].iloc[0]
    open_close_color = alt.condition("datum.open <= datum.close", alt.value("#06982d"), alt.value("#ae1325"))
    base = alt.Chart(df).encode(alt.X('date', axis=alt.Axis(labelOverlap=True, title='Time')), color=open_close_color)
    rule = base.mark_rule().encode(alt.Y('low', title='Price ($)', scale=alt.Scale(zero=False),), alt.Y2('high'))
    bar = base.mark_bar().encode(alt.Y('open'), alt.Y2('close'))
    line = base.mark_line().encode(alt.Y('open_day'))
    st.altair_chart((rule + bar), use_container_width=True)

    st.subheader(symbol+' Daily Chart')
    st.image("https://finviz.com/chart.ashx?t="+symbol)


if option == 'Rally Base Rally All':
    symbol = st.sidebar.selectbox("Symbol", ('SPY', 'QQQ', 'AAPL', 'MSFT', 'NIO', 'AMD', 'NVDA', 'BA', 'CCIV', 'BABA', 'NKE', 'DIS', 'FB', 'OXY', 'TWTR', 'TSLA'), 0)
    rally_percentage = st.sidebar.markdown("Minimum Percentage for Candle to be considered a **Rally: "+str(rally_percentage)+"**")
    st.sidebar.markdown("(open_close Column)")
    st.sidebar.markdown("")
    st.sidebar.markdown("Maximum Percentage of Basing candle drop to Rally candle Rise: **"+str(basing_percentage)+"**")
    st.sidebar.markdown("the larger the percentage the larger the red basing candle")
    st.sidebar.markdown("(basing_percent Column)")

    st.title("Rally Base Rally All Stocks")
    df = pd.read_csv('dist/historical_data.csv')
    last_time = df['date'].values[-2]
    watch_list = df[(df['onWatch'] == 1) & (df['date'] >= last_time)]
    watch_list = watch_list[['Symbol','date','open','high','low','open_close','onWatch']]
    df = df[df['Symbol'] == symbol]
    df_rbr = pd.read_csv('dist/rbr.csv')
    df = df[['date','open','high','low','close','open_close','basing_percent','onWatch','rally','base','rbr','Symbol']]
    df_rbr = df_rbr[['date','open','high','low','close','onWatch','Symbol']]
    df_rbr_all = df_rbr
    df_rbr = df_rbr[df_rbr['Symbol'] == symbol]

    def highlight_basing(x):
        if x['onWatch'] == 1:
            return ['background-color: lightyellow'] * len(df_rbr.columns)
        else:
            return ['background-color: white'] * (len(df_rbr.columns))

    def highlight_rbr(x):
        if x['rbr'] == 1:
            return ['background-color: lightgreen'] * len(df.columns)
        elif x['onWatch'] == 1:
            return ['background-color: lightyellow'] * len(df.columns)
        else:
            return ['background-color: white'] * (len(df.columns))


    st.subheader('Historical '+bar_time_frame+' ticker data for '+symbol)
    st.dataframe(df.style.apply(highlight_rbr, axis=1))

    st.subheader('RBR')
    st.dataframe(df_rbr_all.style.apply(highlight_basing, axis=1))
    x = str(int((len(df_rbr_all)/3)))
    st.write(x+' Total RBR')

    if time.localtime().tm_hour < 15:
        st.subheader('Current Stocks on Watch: Need to Wait for Candle to Close Red (open_close column)')
        st.dataframe(watch_list)

    st.subheader(symbol +' ' + bar_time_frame +' Chart')
    st.write("https://www.barchart.com/stocks/quotes/"+symbol+"/interactive-chart")
    df['open_day'] = df['open'].iloc[0]
    open_close_color = alt.condition("datum.open <= datum.close", alt.value("#06982d"), alt.value("#ae1325"))
    base = alt.Chart(df).encode(alt.X('date', axis=alt.Axis(labelOverlap=True, title='Time')), color=open_close_color)
    rule = base.mark_rule().encode(alt.Y('low', title='Price ($)', scale=alt.Scale(zero=False),), alt.Y2('high'))
    bar = base.mark_bar().encode(alt.Y('open'), alt.Y2('close'))
    line = base.mark_line().encode(alt.Y('open_day'))
    st.altair_chart((rule + bar), use_container_width=True)

    st.subheader(symbol+' Daily Chart')
    st.image("https://finviz.com/chart.ashx?t="+symbol)

    st.subheader('RBR Example')
    st.image('images/RBR Example.png')

if option == 'Historical RBR':
    df = pd.read_csv('dist/rbr_count.csv')
    df = df[['Symbol', 'date', 'Count']]
    min = df['date'].min()
    max = df['date'].max()
    min_date = datetime.strptime(df['date'].min(), '%m/%d/%Y')
    max_date = datetime.strptime(df['date'].max(), '%m/%d/%Y')
    days = (max_date - min_date).days
    df_avg = df.groupby(['Symbol'])['Count'].sum().reset_index()
    df_avg['Count'] = np.ceil(df_avg['Count']/days)

    st.title("Historical RBRs from "+min+" to "+max)
    st.dataframe(df)
    st.markdown("")

    bar = alt.Chart(df).mark_bar(size=18).\
        encode(x=alt.X('Symbol', sort='-y'), y=alt.Y('sum(Count)', axis=alt.Axis(title='Count'))).\
        properties(width=700, height=350)
    text = bar.mark_text(baseline='bottom').encode(text='sum(Count)')
    st.altair_chart(bar+text)

    st.subheader("Avg RBRs per Day")
    st.dataframe(df_avg)
    bar2 = alt.Chart(df_avg).mark_bar(size=18).\
        encode(x=alt.X('Symbol', sort='-y'), y=alt.Y('Count', axis=alt.Axis(title='Count'))).\
        properties(width=700, height=350)
    text2 = bar2.mark_text(baseline='bottom').encode(text='Count')
    st.altair_chart(bar2+text2)

