#!/usr/bin/env python
# coding: utf-8

import yfinance as yf
import pandas as pd
#import talib
#import mplfinance as mpf

import time
from datetime import datetime, timedelta

import os
import streamlit as st
import altair as alt


#!pip install TA-Lib mplfinance streamlit yfinance pandas 
    


def update_dashboard():

    stock = yf.Ticker("CL=F")
    news = stock.news
#    print(news)

    df_news = pd.DataFrame()
 

    news_list=[]
    for n in news:
        keys = n['content'].keys()
        dic = {}
        for k in keys:
            if (k=="thumbnail"):
                dic[k] = n['content'][k]['resolutions'][1]['url']
            else:
                dic[k] = n['content'][k]
        news_list.append(dic)



#        df_temp = pd.DataFrame(n['content'])
 #   df_news = pd.DataFrame(news_list)


#    df_news.reset_index(inplace=True)
#    df_news = df_news[['title', 'description', 'summary', 'pubDate', 'isHosted', 'bypassModal', 'previewUrl', 'thumbnail']]
#    ,
#       'provider', 'canonicalUrl', 'clickThroughUrl', 'metadata', 'finance','storyline']]


    with placeholder.container():
        for n in news_list:
            st.subheader(n['title'], anchor=n['previewUrl'])
            col1, col2 = st.columns([1, 3])
            image = n['thumbnail']
            col1.image(image, caption=None) #, width=200)
            col2.write(f"_"+n['pubDate']+"_")
            col2.html(n['summary'])

        st.dataframe(df_news)


# Streamlit setup
st.title("News related to Crude Oil")

placeholder = st.empty()

# Auto-refreshing loop
while True:
    update_dashboard()
    time.sleep(60)
