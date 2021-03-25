# streamlit run streamlit.py
import streamlit as st
import pandas as pd
import altair as alt
from Requirements import rally_percentage, basing_percentage


st.sidebar.title("Interactive Brokers Trading Automation")
option = st.sidebar.selectbox("Which Dashboard?",('Rally Base Rally', 'Rally Base Rally All','Executed Orders', 'Watch List'), 0)

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


    st.subheader('Historical 5 min ticker data for '+symbol)
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
    st.altair_chart((rule + bar + line), use_container_width=True)

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
    last_time = df['date'].values[-1]
    watch_list = df[(df['onWatch'] == 1) & (df['date'] >= last_time)]
    watch_list = watch_list[['Symbol','date','open','high','low','open_close']]
    df = df[df['Symbol'] == symbol]
    df_rbr = pd.read_csv('dist/rbr.csv')
    df_rbr = df_rbr[df_rbr['Symbol'] == symbol]
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


    st.subheader('Historical 5 min ticker data for '+symbol)
    st.dataframe(df.style.apply(highlight_rbr, axis=1))

    st.subheader(symbol+' RBR')
    st.dataframe(df_rbr.style.apply(highlight_basing, axis=1))
    x = str(int((len(df_rbr)/3)))
    st.write(x+' Total RBR for '+symbol)

    st.subheader('Current Stocks on Watch: Need to Wait for Candle to Close Red (open_close column)')
    st.dataframe(watch_list)

    st.subheader(symbol+' 5 min Chart')
    st.write("https://www.barchart.com/stocks/quotes/"+symbol+"/interactive-chart")
    df['open_day'] = df['open'].iloc[0]
    open_close_color = alt.condition("datum.open <= datum.close", alt.value("#06982d"), alt.value("#ae1325"))
    base = alt.Chart(df).encode(alt.X('date', axis=alt.Axis(labelOverlap=True, title='Time')), color=open_close_color)
    rule = base.mark_rule().encode(alt.Y('low', title='Price ($)', scale=alt.Scale(zero=False),), alt.Y2('high'))
    bar = base.mark_bar().encode(alt.Y('open'), alt.Y2('close'))
    line = base.mark_line().encode(alt.Y('open_day'))
    st.altair_chart((rule + bar + line), use_container_width=True)

    st.subheader(symbol+' Daily Chart')
    st.image("https://finviz.com/chart.ashx?t="+symbol)

    st.subheader('RBR Example')
    st.image('RBR Example.png')