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

ta_indicators = {

    "Volatility" : {
        "Bollinger Bands": 
            {"description": "Bollinger Bands (Lower Band)", "value": 'volatility_bbl', "signal" : 'Bollinger_Bands'},
        "Keltner Channel":
            {"description": "Keltner Channel (Lower Band)", "value": 'volatility_kcl', "signal" : 'Keltner_Channel'}, 
        "Donchian Channel":
            {"description": "Donchian Channel (Lower Band)", "value": 'volatility_dcl', "signal" : 'Donchian_Channel'}, 
        "ATR":  
            {"description": "Average True Range", "value": 'volatility_atr', "signal" : 'ATR' }, 
        "Ulcer Index":
            {"description": "Ulcer Index", "value": 'volatility_ui', "signal" : 'Ulcer_Index'}
        },

    "Volume" : {
        "ADI":
            {"description": "Accumulation/Distribution Index", "value": 'volume_adi', "signal" : 'ADI'},
        "OBV":
            {"description": "On-Balance Volume", "value": 'volume_obv', "signal" : 'OBV'}, 
        "CMF":
            {"description": "Chaikin Money Flow", "value": 'volume_cmf', "signal" : 'CMF'},
        "MFI":
            {"description": "Money Flow Index", "value": 'volume_mfi', "signal" : 'MFI'},
        },

    "Momentum" : {
        "RSI": 
            {"description": "Relative Strength Index", "value": 'momentum_rsi', "signal" : 'RSI'},
        "Stochastic RSI":
            {"description": "Stochastic Relative Strength Index", "value": 'momentum_stoch_rsi_k', "signal" : 'Stochastic_RSI'}, 
        "ROC":
            {"description": "Rate of Change", "value": 'momentum_roc', "signal" : 'ROC'},
        },

    "Trend" : {
        "MACD": 
            {"description": "Moving Average Convergence Divergence", "value": 'trend_macd_diff', "signal" : 'MACD'},
        "ADX":
            {"description": "Average Directional Index", "value": 'trend_adx', "signal" : 'ADX'},
        "Ichimoku": 
            {"description": "Ichimoku Cloud (Conversion Line)", "value": 'trend_ichimoku_conv', "signal" : 'Ichimoku'},
        "PSAR":
            {"description": "Parabolic Stop and Reverse", "value": 'trend_psar_up', "signal" : 'PSAR'},
        }

    }

def ta_index(df):

    # Clean nan values
    df = ta.utils.dropna(df)

    # Add all ta features filling nans values
    df = ta.add_all_ta_features(
        df, "open", "high", "low", "close", "volume", fillna=True
    )

    return df


def calculate_volatility_signals(df):
    # Bollinger Bands
    def bollinger_signal(row):
        if row['close'] < row['volatility_bbl']:
            return "Buy"
        elif row['close'] > row['volatility_bbh']:
            return "Sell"
        else:
            return "Neutral"

    # Keltner Channel
    def keltner_signal(row):
        if row['close'] < row['volatility_kcl']:
            return "Buy"
        elif row['close'] > row['volatility_kch']:
            return "Sell"
        else:
            return "Neutral"

    # Donchian Channel
    def donchian_signal(row):
        if row['close'] < row['volatility_dcl']:
            return "Buy"
        elif row['close'] > row['volatility_dch']:
            return "Sell"
        else:
            return "Neutral"

    # ATR (Average True Range)
    df['ATR_Rolling_Mean'] = df['volatility_atr'].rolling(14).mean()
    def atr_signal(row):
        if row['volatility_atr'] > row['ATR_Rolling_Mean']:
            return "Buy"
        elif row['volatility_atr'] < row['ATR_Rolling_Mean']:
            return "Sell"
        else:
            return "Neutral"

    # Ulcer Index
    df['UI_Rolling_Mean'] = df['volatility_ui'].rolling(14).mean()
    def ulcer_signal(row):
        if row['volatility_ui'] < row['UI_Rolling_Mean']:
            return "Buy"
        elif row['volatility_ui'] > row['UI_Rolling_Mean']:
            return "Sell"
        else:
            return "Neutral"

    # Aplicăm funcțiile pentru fiecare indicator de volatilitate
    df['Bollinger_Bands'] = df.apply(bollinger_signal, axis=1)
    df['Keltner_Channel'] = df.apply(keltner_signal, axis=1)
    df['Donchian_Channel'] = df.apply(donchian_signal, axis=1)
    df['ATR'] = df.apply(atr_signal, axis=1)
    df['Ulcer_Index'] = df.apply(ulcer_signal, axis=1)

    return df


# Calculăm semnalele bazate pe indicatorii de volum
def calculate_volume_signals(df):
    # ADI
    df['ADI_Rolling_Mean'] = df['volume_adi'].rolling(14).mean()
    def adi_signal(row):
        if row['volume_adi'] > row['ADI_Rolling_Mean']:
            return "Buy"
        elif row['volume_adi'] < row['ADI_Rolling_Mean']:
            return "Sell"
        else:
            return "Neutral"

    # OBV
    df['OBV_Rolling_Mean'] = df['volume_obv'].rolling(14).mean()
    def obv_signal(row):
        if row['volume_obv'] > row['OBV_Rolling_Mean']:
            return "Buy"
        elif row['volume_obv'] < row['OBV_Rolling_Mean']:
            return "Sell"
        else:
            return "Neutral"

    # CMF
    def cmf_signal(row):
        if row['volume_cmf'] > 0.1:
            return "Buy"
        elif row['volume_cmf'] < -0.1:
            return "Sell"
        else:
            return "Neutral"

    # MFI
    def mfi_signal(row):
        if row['volume_mfi'] < 20:
            return "Buy"
        elif row['volume_mfi'] > 80:
            return "Sell"
        else:
            return "Neutral"

    # Aplicăm funcțiile pentru fiecare indicator de volum
    df['ADI'] = df.apply(adi_signal, axis=1)
    df['OBV'] = df.apply(obv_signal, axis=1)
    df['CMF'] = df.apply(cmf_signal, axis=1)
    df['MFI'] = df.apply(mfi_signal, axis=1)

    return df

# Calculăm semnalele bazate pe indicatorii de momentum
def calculate_momentum_signals(df):
    # RSI
    def rsi_signal(row):
        if row['momentum_rsi'] < 30:
            return "Buy"
        elif row['momentum_rsi'] > 70:
            return "Sell"
        else:
            return "Neutral"

    # Stochastic RSI
    def stoch_rsi_signal(row):
        if row['momentum_stoch_rsi_k'] < 20:
            return "Buy"
        elif row['momentum_stoch_rsi_k'] > 80:
            return "Sell"
        else:
            return "Neutral"

    # ROC
    def roc_signal(row):
        if row['momentum_roc'] > 0:
            return "Buy"
        elif row['momentum_roc'] < 0:
            return "Sell"
        else:
            return "Neutral"

    # Aplicăm funcțiile pentru fiecare indicator de momentum
    df['RSI'] = df.apply(rsi_signal, axis=1)
    df['Stochastic_RSI'] = df.apply(stoch_rsi_signal, axis=1)
    df['ROC'] = df.apply(roc_signal, axis=1)

    return df

# Calculăm semnalele bazate pe indicatorii de trend
def calculate_trend_signals(df):
    # MACD
    def macd_signal(row):
        if row['trend_macd_diff'] > 0:
            return "Buy"
        elif row['trend_macd_diff'] < 0:
            return "Sell"
        else:
            return "Neutral"

    # ADX
    def adx_signal(row):
        if row['trend_adx'] > 25:
            if row['trend_adx_pos'] > row['trend_adx_neg']:
                return "Buy"
            else:
                return "Sell"
        else:
            return "Neutral"

    # Ichimoku Cloud
    def ichimoku_signal(row):
        if row['trend_ichimoku_conv'] > row['trend_ichimoku_base']:
            return "Buy"
        elif row['trend_ichimoku_conv'] < row['trend_ichimoku_base']:
            return "Sell"
        else:
            return "Neutral"

    # Parabolic SAR
    def psar_signal(row):
        if row['close'] > row['trend_psar_down']:
            return "Buy"
        elif row['close'] < row['trend_psar_up']:
            return "Sell"
        else:
            return "Neutral"

    # Aplicăm funcțiile pentru fiecare indicator de trend
    df['MACD'] = df.apply(macd_signal, axis=1)
    df['ADX'] = df.apply(adx_signal, axis=1)
    df['Ichimoku'] = df.apply(ichimoku_signal, axis=1)
    df['PSAR'] = df.apply(psar_signal, axis=1)

    return df




# Define a function to generate trade signals and signal direction based on indicator values
def get_trade_signal_and_direction(indicator, value):
    if 'rsi' in indicator:
        if value < 30:
            return 'Oversold', 'Positive'
        elif value > 70:
            return 'Overbought', 'Negative'
        else:
            return 'Neutral', 'Neutral'
    elif 'stoch' in indicator:
        if value < 20:
            return 'Oversold', 'Positive'
        elif value > 80:
            return 'Overbought', 'Negative'
        else:
            return 'Neutral', 'Neutral'
    elif 'macd' in indicator:
        if value > 0:
            return 'Bullish Trend', 'Positive'
        elif value < 0:
            return 'Bearish Trend', 'Negative'
        else:
            return 'Neutral', 'Neutral'
    elif 'bollinger' in indicator:
        if 'hband' in indicator:
            return 'Upper Band', 'Negative'
        elif 'lband' in indicator:
            return 'Lower Band', 'Positive'
        else:
            return 'Neutral', 'Neutral'
    else:
        return 'No Signal', 'Neutral'



def signal(df):

# Create a list to store the table data
    table_data = []

    yf_data_with_ta = ta.add_all_ta_features(
        df=df, 
        open='open', 
        high='high', 
        low='low', 
        close='close', 
        volume='volume', 
        fillna=True
    )
# Iterate over the columns in the dataframe to extract indicator information
    for col in yf_data_with_ta.columns:
        if col not in ['date', 'open', 'high', 'low', 'close', 'volume']:
            indicator_value = yf_data_with_ta[col].iloc[-1]
            signal, direction = get_trade_signal_and_direction(col, indicator_value)
            table_data.append([
                'Group Placeholder',  # Placeholder for Technical Indicators group
                col,  # Technical Indicator code
                col.replace('_', ' ').title(),  # Technical Indicator name
                indicator_value,  # Technical Indicator value
                signal,  # Trade Signal
                direction  # Signal direction
            ])

    # Create a DataFrame for the final table
    columns = [
        "Group", "Code", "Name",
        "Value", "Signal", "Direction"
    ]
    
    final_df = pd.DataFrame(table_data, columns=columns)

# Display the resulting table
    return final_df

def color_signal(val):

    if (val=="Buy"): 
        color = 'green' 
    elif (val=="Sell"):
        color = 'red'
    else:
        color = "black"
    return f'color: {color}'
# background-color

def center_text(tex, size, color):
    st.markdown(f"<h{size} style='text-align: center; color: {color}'>{tex}</h{size}>",
            unsafe_allow_html=True)


def gauge_diagram(df):

    signal_map = {
        'Strong Buy': 6,
        'Buy': 3,
        'Sell': -3,
        'Strong Sell': -6,
        'Neutral': 0
    }

    # Calculate total signal
    df['Signal Value'] = df['Signal'].map(signal_map)

    count_signal = 0
    sum_signal=0

    for key, value in signal_map.items():

#        print('key:', key, ' value:', value)
#        print('count_signal:', df[df['Signal']==key]['Signal Value'].count())
#        print('sum_signal',df[df['Signal']==key]['Signal Value'].sum())

        count_signal = count_signal + df[df['Signal']==key]['Signal Value'].count() 
        sum_signal = sum_signal + df[df['Signal']==key]['Signal Value'].sum()


    count_signal = df[df['Signal Value']!=0]['Signal Value'].count() 
    sum_signal = df['Signal Value'].sum()


    sum_signal_buy = df[df['Signal Value']>0]['Signal Value'].count()
    sum_signal_sell = df[df['Signal Value']<0]['Signal Value'].count()
    sum_signal_neutral = df[df['Signal Value']==0]['Signal Value'].count()


    if (sum_signal_sell>sum_signal_buy):
        total_signal = -1
    elif (sum_signal_sell<sum_signal_buy):
        total_signal = 1
    else:
        total_signal = 0



#    print('count_signal:', count_signal, 'sum_signal:', sum_signal)
    if (count_signal>0):
        total_signal = (sum_signal/count_signal) / 2
    else:
        total_signal = 0


#    print('total_signal:', total_signal)

#    df['Signal Value'].sum()

    if (total_signal<=-1.5):
        signal = "Strong Sell"
    elif ((total_signal>-1.5) & (total_signal<=-0.5)):
        signal = "Sell"
    elif ((total_signal>-0.5) & (total_signal<0.5)):
        signal = "Neutral"
    elif ((total_signal>=0.5) & (total_signal<1.5)):
        signal = "Buy"
    elif (total_signal>=1.5):
        signal = "Strong Buy"


    colors = ["#72c66e", "#c1da64", "#f6ee54", "#fabd57", "#f36d54"]
    values = [2.5,1.5,0.5,-0.5,-1.5,-2.5]

    x_axis_vals = [0, 0.628, 1.256, 1.88, 2.5]

    fig = plt.figure(figsize=(18,18))

    ax = fig.add_subplot(projection="polar");

    ax.bar(x=[0, 0.628, 1.256, 1.88, 2.5], width=0.6, height=0.6, bottom=2,
       linewidth=3, edgecolor="white",
       color=colors, align="edge");

    plt.annotate("Strong Buy", xy=(0.16,2.1), rotation=-73, color="black", fontsize=18, fontweight="bold");
    plt.annotate("Buy", xy=(0.89,2.1), rotation=-40, color="black", fontsize=18, fontweight="bold");
    plt.annotate("Neutral", xy=(1.6,2.2),  color="black", fontsize=18, fontweight="bold");
    plt.annotate("Sell", xy=(2.28,2.25), rotation=40,color="black", fontsize=18, fontweight="bold");
    plt.annotate("Strong Sell", xy=(2.93,2.25), rotation=74, color="black", fontsize=18, fontweight="bold");

    plt.annotate(signal, xytext=(0,0), xy=(1.57-(total_signal/2)*1.57, 2.0),
             arrowprops=dict(arrowstyle="wedge, tail_width=0.5", color="black", shrinkA=0),
             bbox=dict(boxstyle="circle", facecolor="black", linewidth=2.0, ),
             fontsize=45, color="white", ha="center"
            );


    plt.title("Technical Analysis", loc="center", pad=20, fontsize=35, fontweight="bold");

    ax.set_axis_off();

    st.write("Summary: {}  &nbsp;&nbsp;&nbsp;&nbsp;  Buy: {}  &nbsp;&nbsp;&nbsp;&nbsp;  Neutral: {}  &nbsp;&nbsp;&nbsp;&nbsp;  Sell: {}".format(signal, sum_signal_buy, sum_signal_neutral, sum_signal_sell))

    st.pyplot(fig)



def update_dashboard():


    next_month=(datetime.now().replace(day=1)+timedelta(days=32)) #.replace(day=1)+timedelta(days=-1)
    st.title("Crude Oil "+next_month.strftime("%B")+" "+symbol)

    st.session_state["tabs"] = ["5 minutes", "1 hour", "1 day"]
    tabs = st.tabs(st.session_state["tabs"])


    with tabs[0]:
    
        tabs[0].subheader("Technical Analysis for 5 minutes interval")

        try:
            df_5m = pd.read_csv("./data/yf_data_5m.csv")
        except:
            df_5m =  utils.read_data(symbol, "max", "5m")

        df_m=df_5m.copy()

        # Descărcăm și procesăm datele
        df_m = ta_index(df_m)
        df_m = calculate_volatility_signals(df_m)  # Semnale pentru volatilitate
        df_m = calculate_volume_signals(df_m)  # Semnale pentru volum
        df_m = calculate_momentum_signals(df_m)  # Semnale pentru momentum
        df_m = calculate_trend_signals(df_m)  # Semnale pentru trend

        all_ta = pd.DataFrame()

        for ta_k, ta_value in ta_indicators.items():

            st.write("### "+ta_k)

            ta_signals = []
            for indicator_name, indicator_values in ta_value.items():
                signal ={
                "Indicator": indicator_name,
                "Description": indicator_values['description'],
                "Value": df_m[indicator_values['value']].iloc[-1],
                "Signal": df_m[indicator_values['signal']].iloc[-1],
                }

                ta_signals.append(signal)

            df_ta = pd.DataFrame(ta_signals)
            all_ta = pd.concat([all_ta, df_ta])

            st.dataframe(df_ta.style.applymap(color_signal, subset=['Signal']), hide_index=True)

        gauge_diagram(all_ta)


    with tabs[1]:

#        tabs[0].subheader("Technical Analysis for 1 hour interval")

        st.write("### Technical Analysis for 1 hour interval")


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

#        tabs[0].subheader("Technical Analysis for 1 day interval")
        st.write("### Technical Analysis for 1 day interval")

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
