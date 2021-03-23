# streamlit run streamlit.py
import streamlit as st
import requests
import pandas as pd
import altair as alt


st.sidebar.title("Interactive Brokers Trading Automation")
option = st.sidebar.selectbox("Which Dashboard?",('Rally Base Rally', 'Executed Orders', 'Watch List', 'Stocktwits'), 0)

if option == 'Rally Base Rally':
    symbol = st.sidebar.selectbox("Symbol", ('SPY', 'QQQ', 'AAPL', 'MSFT', 'NIO', 'AMD', 'NVDA', 'BA', 'CCIV', 'BABA', 'NKE', 'DIS', 'FB', 'OXY', 'GME', 'TWTR', 'TSAL'), 0)
    st.title("Rally Base Rally")
    df = pd.read_csv('historical_data.csv')
    watch_list = df[df['onWatch'] == 1]
    watch_list = watch_list[['date','open','high','low','Symbol']]
    df = df[df['Symbol'] == symbol]
    df_rbr = pd.read_csv('rbr.csv')
    df_rbr = df_rbr[df_rbr['Symbol'] == symbol]
    df = df.iloc[:, 1:9]
    df_rbr = df_rbr[['date','open','high','low','onWatch']]

    def highlight_basing(x):
        if x['onWatch'] == 1:
            return ['background-color: lightgrey'] * 5
        else:
            return ['background-color: white'] * 5

    def highlight_rbr(x):
        if x['rbr'] == 1:
            return ['background-color: lightgreen'] * 8
        elif x['onWatch'] == 1:
            return ['background-color: lightyellow'] * 8
        else:
            return ['background-color: white'] * 8

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

    st.subheader('Current Stocks on Watch')
    st.dataframe(watch_list)


if option == 'Watch List':
    st.title('Watch list')
    st.write("https://www.google.com/finance/quote/AAPL:NASDAQ")
    df_watch_list = pd.DataFrame(columns=['Symbol','Last Trade Price','Previous Close','Index'])
    st.dataframe(df_watch_list)


if option == 'Stocktwits':
    st.title('Stocktwits')
    symbol = st.sidebar.text_input("Symbol", value='SPY', max_chars=5)
    r = requests.get(f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json")
    data = r.json()
    for message in data['messages']:
        st.image(message['user']['avatar_url'])
        st.write(message['user']['username'])
        st.write(message['created_at'])
        st.write(message['body'])