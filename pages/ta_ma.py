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

import ta
from ta.utils import dropna

import utils


import plotly.graph_objects as go

import matplotlib.pyplot as plt


symbol="CL=F"


def get_ma_RS(df, window):

    # Calculate the moving average
    df['ma']=df['close'].rolling(window=window).mean()

    # Identify the points where the moving average acted as support
    df['support'] = (df['low'] <= df['ma']) & (df['close'] > df['ma'])

    # Identify the points where the moving average acted as resistance
    df['resistance'] = (df['high'] >= df['ma']) & (df['close'] < df['ma'])
    
    return df


def get_pivots(df):

    #df sould be a pandas dataframe with open/high/low/close columns

    high = df['high'].max()
    low = df['low'].min()
    close = df['close'][-1]
    
    # Calculate the pivot point based on the previous day high, low, close
    pivot = (high + low + close) / 3

    # Calculate the support and resistance levels
    support1=2 * pivot - high
    support2 = pivot - (high - low)
    support3= low - 2 * (high - pivot)

    resistance1 = 2 * pivot - low
    resistance2 = pivot+ (high - low)
    resistance3 = high+ 2 * (pivot - low)
    
    return {'pivot':pivot, 
            'support1':support1, 
            'support2':support2, 
            'support3':support3,
            'resistance1':resistance1, 
            'resistance2':resistance2, 
            'resistance3':resistance3}



def get_fibo_SR(df):
    
    # Identify the high and low swing points
    high = df['high'].max()
    low = df['low'].min()

    # Calculate the key Fibonacci levels
    fibonacci_levels = [23.6, 38.2, 50, 61.8, 100]
    fibonacci_levels = [level / 100 for level in fibonacci_levels]
    fibonacci_levels = [low + (high - low) * level for level in fibonacci_levels]
    
    return fibonacci_levels

def update_dashboard():


    next_month=(datetime.now().replace(day=1)+timedelta(days=32)) #.replace(day=1)+timedelta(days=-1)
    st.title("Crude Oil "+next_month.strftime("%B")+" ("+symbol+")")
    st.write("#### Technical Analysis")

    st.session_state["tabs"] = ["5 minutes", "1 hour", "1 day"]
    tabs = st.tabs(st.session_state["tabs"])

    with tabs[0]:

        tabs[0].write("##### Moving Averages for 5 minutes interval")

        try:
            df_5m =  utils.read_data(symbol, "max", "5m")
        except:
            df_5m = pd.read_csv("./data/yf_data_5m.csv")

        df_5m = df_5m[-720:]

        df_m=df_5m[df_5m['volume']!=0].copy()

        # extract the first 200 rows of the dataset
        df_m = get_ma_RS(df_m.head(200), 20)

        fig = go.Figure(data=go.Ohlc(x=df_5m['date'],  # .index
                             open=df_5m['open'],
                             high=df_5m['high'],
                             low=df_5m['low'],
                             close=df_5m['close']))

        # plot the moving average
        trace= go.Scatter(x=df_m['date'], y=df_m['ma'], mode='lines', name='MA20')
        fig.add_trace(trace)

        # get the resistance and support values
        resistances= df_m.loc[df_m['resistance'], 'ma']
        supports= df_m.loc[df_m['support'], 'ma']

        print('resistances:', resistances)
        print('supports:', supports)

        # plot the resistances
        for r in resistances:
   
            fig.add_hline(y=r, line_width=1, line_dash="dash", line_color="red")

            fig.add_annotation(
                x=df_m['date'][0]   #.index[0]
                , y=r
                , text="R"
                , yanchor='bottom'
                , font=dict(size=12, color="red", family="Sans Serif")
                , align="left"
            ,)
    
        # plot the supports
        for s in supports:
   
            fig.add_hline(y=s, line_width=1, line_dash="dash", line_color="green")

            fig.add_annotation(
                x=df_m['date'][0]   #.index[0]
                , y=s
                , text="S"
                , yanchor='bottom'
                , font=dict(size=12, color="green", family="Sans Serif")
                , align="right"
                ,)

        # remove the rangeslider
        fig.update_layout(xaxis_rangeslider_visible=False)

        # show the figure
#        fig.show()

        st.plotly_chart(fig)

    with tabs[1]:

        tabs[1].write("##### Moving Averages 1 hour interval")

        try:
            df_1h =  utils.read_data(symbol, "max", "1h")
        except:
            df_1h = pd.read_csv("./data/yf_data_1h.csv")

        df_1h = df_1h[-720:]

        df_h=df_1h[df_1h['volume']!=0].copy()

        # extract the first 200 rows of the dataset
        df = get_ma_RS(df_1h.head(200), 20)

        fig = go.Figure(data=go.Ohlc(x=df_h['date'],   # .index
                             open=df_h['open'],
                             high=df_h['high'],
                             low=df_h['low'],
                             close=df_h['close']))

        # plot the moving average
        trace= go.Scatter(x=df['date'], y=df['ma'], mode='lines', name='MA20')
        fig.add_trace(trace)

        # get the resistance and support values
        resistances= df.loc[df['resistance'], 'ma']
        supports= df.loc[df['support'], 'ma']

        print('resistances:', resistances)
        print('supports:', supports)

        # plot the resistances
        for r in resistances:
   
            fig.add_hline(y=r, line_width=1, line_dash="dash", line_color="red")

            fig.add_annotation(
                x=df['date'][0]  #.index[0]
                , y=r
                , text="R"
                , yanchor='bottom'
                , font=dict(size=12, color="red", family="Sans Serif")
                , align="left"
            ,)
    
        # plot the supports
        for s in supports:
   
            fig.add_hline(y=s, line_width=1, line_dash="dash", line_color="green")

            fig.add_annotation(
                x=df['date'][0]  #.index[0]
                , y=s
                , text="S"
                , yanchor='bottom'
                , font=dict(size=12, color="green", family="Sans Serif")
                , align="left"
                ,)

        # remove the rangeslider
        fig.update_layout(xaxis_rangeslider_visible=False)

        # show the figure
#        fig.show()

        st.plotly_chart(fig)



    with tabs[2]:
        tabs[2].write("##### Moving Averages for 1 day interval")


        try:
            df_1d =  utils.read_data(symbol, "max", "1d")
        except:
            df_1d = pd.read_csv("./data/yf_data_1d.csv")

#        df_d=df_1d.copy()

        df_1d = df_1d[-720:]

        df = get_ma_RS(df_1d.head(240), 20)

        fig = go.Figure(data=go.Ohlc(x=df_1d['date'],   # .index
                             open=df_1d['open'],
                             high=df_1d['high'],
                             low=df_1d['low'],
                             close=df_1d['close']))

        # plot the moving average
        trace= go.Scatter(x=df['date'], y=df['ma'], mode='lines', name='MA20')
        fig.add_trace(trace)

        # get the resistance and support values
        resistances= df.loc[df['resistance'], 'ma']
        supports= df.loc[df['support'], 'ma']

        print('resistances:', resistances)
        print('supports:', supports)

        # plot the resistances
        for r in resistances:
   
            fig.add_hline(y=r, line_width=1, line_dash="dash", line_color="red")

            fig.add_annotation(
                x=df['date'][0]  #.index[0]
                , y=r
                , text="R"
                , yanchor='bottom'
                , font=dict(size=12, color="red", family="Sans Serif")
                , align="left"
            ,)
    
        # plot the supports
        for s in supports:
   
            fig.add_hline(y=s, line_width=1, line_dash="dash", line_color="green")

            fig.add_annotation(
                x=df['date'][0]  #.index[0]
                , y=s
                , text="S"
                , yanchor='bottom'
                , font=dict(size=12, color="green", family="Sans Serif")
                , align="left"
                ,)

        # remove the rangeslider
        fig.update_layout(xaxis_rangeslider_visible=False)

        # show the figure
#        fig.show()

        st.plotly_chart(fig)


def main():
    
    output_type=None
#    while True:
#        update_dashboard()
#        time.sleep(60)

    output = update_dashboard()


#if __name__ == "__main__":
main()
