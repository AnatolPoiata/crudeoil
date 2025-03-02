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


def get_ma_RS(df):

    # Calculate the moving average
    df['ma']=df['close'].rolling(window=20).mean()

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
    st.subtitle("Technical Analysis")

    st.session_state["tabs"] = ["5 minutes", "1 hour", "1 day"]
    tabs = st.tabs(st.session_state["tabs"])

    with tabs[0]:

        tabs[0].subheader("Support & Risistance for 5 minutes interval")

        try:
            df_5m = pd.read_csv("./data/yf_data_5m.csv")
        except:
            df_5m =  utils.read_data(symbol, "max", "5m")

        df_m=df_5m.copy()


        # extract the first 200 rows of the dataset
        df = get_ma_RS(df1.head(200))

        fig = go.Figure(data=go.Ohlc(x=df1.index,
                             open=df1['open'],
                             high=df1['high'],
                             low=df1['low'],
                             close=df1['close']))

        # plot the moving average
        trace= go.Scatter(x=df.index, y=df['ma'], mode='lines', name='MA20')
        fig.add_trace(trace)

        # get the resistance and support values
        resistances= df.loc[df['resistance'], 'ma']
        supports= df.loc[df['support'], 'ma']

        # plot the resistances
        for r in resistances:
   
            fig.add_hline(y=r, line_width=1, line_dash="dash", line_color="red")

            fig.add_annotation(
                x=df.index[0]
                , y=r
                , text="R"
                , yanchor='bottom'
                , font=dict(size=12, color="red", family="Sans Serif")
                , align="left"
            ,)
    
        # plot the supports
        for s in supports:
   
            fig.add_hline(y=r, line_width=1, line_dash="dash", line_color="green")

            fig.add_annotation(
                x=df.index[0]
                , y=r
                , text="S"
                , yanchor='bottom'
                , font=dict(size=12, color="green", family="Sans Serif")
                , align="left"
                ,)

        # remove the rangeslider
        fig.update_layout(xaxis_rangeslider_visible=False)

        # show the figure
#        fig.show()

        st.pyplot(fig)

    with tabs[1]:

        tabs[1].subheader("Support & Risistance for 1 hour interval")

        try:
            df_1h = pd.read_csv("./data/yf_data_1h.csv")
        except:
            df_1h =  utils.read_data(symbol, "max", "1h")

        df_h=df_1h.copy()

        # Descărcăm și procesăm datele
        df_h = ta_index(df_h)
        df_h = calculate_volatility_signals(df_h)  # Semnale pentru volatilitate
        df_h = calculate_volume_signals(df_h)  # Semnale pentru volum
        df_h = calculate_momentum_signals(df_h)  # Semnale pentru momentum
        df_h = calculate_trend_signals(df_h)  # Semnale pentru trend


        for ta_k, ta_value in ta_indicators.items():

            st.write("### "+ta_k)

            ta_signals = []
            for indicator_name, indicator_values in ta_value.items():
                signal ={
                "Indicator": indicator_name,
                "Description": indicator_values['description'],
                "Value": df_h[indicator_values['value']].iloc[-1],
                "Signal": df_h[indicator_values['signal']].iloc[-1],
                }

                ta_signals.append(signal)
            df_ta = pd.DataFrame(ta_signals)

            st.dataframe(df_ta.style.applymap(color_signal, subset=['Signal']), hide_index=True)


    with tabs[2]:
        tabs[2].subheader("Support & Risistance for 1 day interval")


        try:
            df_1d = pd.read_csv("./data/yf_data_1d.csv")
        except:
            df_1d =  utils.read_data(symbol, "max", "1d")

        df_d=df_1d.copy()

        # Descărcăm și procesăm datele
        df_d = ta_index(df_d)
        df_d = calculate_volatility_signals(df_d)  # Semnale pentru volatilitate
        df_d = calculate_volume_signals(df_d)  # Semnale pentru volum
        df_d = calculate_momentum_signals(df_d)  # Semnale pentru momentum
        df_d = calculate_trend_signals(df_d)  # Semnale pentru trend

        for ta_k, ta_value in ta_indicators.items():

            st.write("### "+ta_k)

            ta_signals = []
            for indicator_name, indicator_values in ta_value.items():
                signal ={
                "Indicator": indicator_name,
                "Description": indicator_values['description'],
                "Value": df_d[indicator_values['value']].iloc[-1],
                "Signal": df_d[indicator_values['signal']].iloc[-1],
                }

                ta_signals.append(signal)
            df_ta = pd.DataFrame(ta_signals)

            st.dataframe(df_ta.style.applymap(color_signal, subset=['Signal']), hide_index=True)



def main():
    
    output_type=None
#    while True:
#        update_dashboard()
#        time.sleep(60)

    output = update_dashboard()


#if __name__ == "__main__":
main()
