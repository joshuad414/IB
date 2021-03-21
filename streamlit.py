# streamlit run streamlit.py
import streamlit as st
import requests
import pandas as pd
import numpy as np

st.title("Interactive Brokers Trading Automation")
st.sidebar.title("Options")
option = st.sidebar.selectbox("Which Dashboard?",('Rally Base Rally', 'Executed Orders', 'Stocktwits'), 1)

if option == 'Rally Base Rally':
    df = pd.read_csv('historical_data.csv')
    df_rbr = pd.read_csv('rbr.csv')
    stock = df['Symbol'][0]
    df = df.iloc[:, 1:6]
    df_rbr = df_rbr[['date','open','high','low','onWatch']]

    st.header('Rally Base Rally')
    st.subheader('Historical 5 min ticker data for '+ stock)
    st.dataframe(df)
    st.subheader(stock+' RBR')
    st.dataframe(df_rbr)
    st.subheader(stock+' Daily Chart')
    st.image("https://finviz.com/chart.ashx?t="+stock)
    st.write("https://www.barchart.com/stocks/quotes/"+stock+"/interactive-chart")

if option == 'Stocktwits':
    st.header('Stocktwits')
    symbol = st.sidebar.text_input("Symbol", value='SPY', max_chars=5)
    r = requests.get(f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json")
    data = r.json()
    for message in data['messages']:
        st.image(message['user']['avatar_url'])
        st.write(message['user']['username'])
        st.write(message['created_at'])
        st.write(message['body'])