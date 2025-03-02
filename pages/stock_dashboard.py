#!/usr/bin/env python
# coding: utf-8

import yfinance as yf
import pandas as pd
#import talib
#import mplfinance as mpf

import time
from datetime import datetime, timedelta
from datetime import timezone 

from pytz import timezone as tz

import os
import streamlit as st
import altair as alt

import utils


symbol="CL=F"

#!pip install TA-Lib mplfinance streamlit yfinance pandas 
	
def historic_data(symbol, period, interval):


	if interval == '1m':
		period = 'max'
	elif interval == '5m':
		period = '1mo'
	elif interval == '1h':
		period = '2y'
	else:
		period = 'max'


	try:
#		if (start):
#			df = yf.download(symbol, start=start, end=end, interval=interval)
#		else:

		df = yf.download(symbol, period=period, interval=interval)

#		print(df.head())
#		print(df.tail())

		cl= list(df.columns.levels[0])
		df.columns = [None] * len(df.columns)
		df = df.drop([0, 1], errors='ignore').reset_index(drop=False)

		df.columns= ['date'] + [x.lower() for x in cl] #, 'close', 'high', 'low', 'open', 'volume']

		# Convertim coloana 'Date' într-un obiect de tip datetime
		df['date'] = pd.to_datetime(df['date'])
		# Setăm coloana 'Date' ca index pentru a ușura manipularea datelor
		df.set_index('date', inplace=True)

		# Calculăm diferența dintre fiecare două timestampuri consecutive
		time_diff = df.index.to_series().diff()

		if (interval=="5m"):
			df = df.resample('5min').last()
		elif (interval=="1m"):
			df = df.resample('1min').last()
		elif (interval=="1h"):
			df = df.resample('1h').last()
		else :
			df = df.resample('1D').last()

		df['open'] = pd.to_numeric(df['open'], errors='coerce')
		df['high'] = pd.to_numeric(df['high'], errors='coerce')
		df['low'] = pd.to_numeric(df['low'], errors='coerce')
		df['close'] = pd.to_numeric(df['close'], errors='coerce')
		df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

		df = df.interpolate(method='linear', limit_direction='both')
		df['date'] = df.index
		df.reset_index(drop=True, inplace=True)

		df.to_csv("./data/yf_data_"+interval+".csv", index=False)

	except Exception as e:
		print(e)
		input('error read historic data')
		df=pd.read_csv("./data/yf_data_"+interval+".csv")

	return df[['date','open', 'high', 'low', 'close','volume']]


def update_forecast(tr, interval):

	try:
#		df_history = utils.read_data(symbol, "max", interval)
		df_history = pd.read_csv("./data/yf_data_"+interval+".csv")
	except:
		print("Missing History data")

	try:
		df_forecast = pd.read_csv("./data/forecast_"+interval+".csv")
	except:
		df_forecast = pd.DataFrame()


	df_history['date'] = df_history['date'].apply(lambda x: str(x).split("+")[0])

	if (interval=="5m"):
		data_format = '%Y-%m-%d %H:%M:%S'
	elif (interval=="1h"):
		data_format = '%Y-%m-%d %H:%M:%S'
	else:
		df_history['date'] = df_history['date'].apply(lambda x: str(x).split(" ")[0])
		data_format = '%Y-%m-%d'



#	df_history = pd.concat([df_history, df_forecast])
#	try:
	df_history['date'] = pd.to_datetime(df_history['date'], format=data_format)
#	except Exception as e:
#		print(e)
#		df_history['date'] = pd.to_datetime(df_history['date'], format='%Y-%m-%d')


	df_history.drop_duplicates(subset='date', inplace=True)
	df_history.reset_index(inplace=True)

	actual_time = datetime.now(timezone.utc) 
	last_time = df_forecast['date'].tolist()[-1]  #.max()
	last_time = str(last_time).split("+")[0]
	last_time = datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz('UTC'))

	minutes = (actual_time - last_time).total_seconds() / 60

#	print('minutes:', minutes)

	if (minutes<-1):
		new_forecast = df_history[tr].tolist()[-1]
		old_forecast = df_history[tr].tolist()[-2]
		try:
			forecast_date = df_forecast['date'].tolist()[-1]  #.max().strftime("%Y-%m-%d %H:%M")
		except:
			forecast_date = df_history['date'].tolist()[-1] #.max().strftime("%Y-%m-%d %H:%M")	
#		forecast_date = forecast['date'].tolist()[-1]		
		return new_forecast, old_forecast, forecast_date

	df_history = utils.read_data(symbol, "max", interval)
	df_history['date'] = df_history['date'].apply(lambda x: str(x).split("+")[0])

	if (interval=="5m"):
		data_format = '%Y-%m-%d %H:%M:%S'
	elif (interval=="1h"):
		data_format = '%Y-%m-%d %H:%M:%S'
	else:
		df_history['date'] = df_history['date'].apply(lambda x: str(x).split(" ")[0])
		data_format = '%Y-%m-%d'

	df_history['date'] = pd.to_datetime(df_history['date'], format=data_format)

	forecast = utils.apply_model(df_history[['date', tr]], tr, interval)
#	print('forecast:', forecast)

	if (forecast.shape[0]!=0):
		forecast.reset_index(inplace=True)
		forecast = pd.concat([df_forecast[['date', tr]], forecast[['date', tr]]])
		forecast.drop_duplicates(subset='date', inplace=True)
		forecast[['date', tr]].to_csv("./data/forecast_"+interval+".csv", index=False)
	else:
		forecast = df_history.copy()
		forecast = df_history.copy()

	new_forecast = forecast[tr].tolist()[-1]
	old_forecast = forecast[tr].tolist()[-2]

#	forecast_date = forecast['date'].max().strftime("%Y-%m-%d %H:%M")
	forecast_date = forecast['date'].tolist()[-1]

	return new_forecast, old_forecast, forecast_date


def update_dashboard():
	global old_value

	new_1d, old_1d, forecast_date_1d = update_forecast("close", "1d")
	new_1h, old_1h, forecast_date_1h = update_forecast("close", "1h")
	new_5m, old_5m, forecast_date_5m = update_forecast("close", "5m")

	start = (datetime.now()+timedelta(days=-1)).strftime("%Y-%m-%d")
	end = datetime.now().strftime("%Y-%m-%d")

	df_historic_1m = historic_data(symbol, "5d", "1m") #, start=start, end=end)

	df_test = df_historic_1m.copy()

#	print(df_historic_1m.head())
#	print(df_historic_1m.tail())

	df_historic_1m = df_historic_1m[-60:]
	df_historic_1m['hour (UTC)'] = df_historic_1m['date'].apply(lambda x: x.strftime("%H:%M"))
	df_historic_1m['day'] = df_historic_1m['date'].apply(lambda x: x.strftime("%Y-%m-%d"))



	min_value=df_historic_1m['close'].min()
	max_value=df_historic_1m['close'].max()

#	stock = yf.Ticker(symbol)

	# Display results in Streamlit

	with placeholder.container():

#		print(df_historic_1m.tail())

		try:
			current_value = round(df_historic_1m['close'].tolist()[-1],2)
		except:
			print('No current_value')
			print(df_historic_1m.head())
			print(df_test.head())
			print('symbol=', symbol)
			current_value = 0

		refresh_time = df_historic_1m['date'].tolist()[-1].strftime("%Y-%m-%d %H:%M")   # .max()
#		refresh_time = df_historic_1m['date'].max()


#		round(stock.fast_info.last_price,2)
		st.write(f"As of {refresh_time} (UTC)") #. Market Open")

		if (old_value == 0):
			old_value = current_value
#			round(stock.fast_info.last_price,2)

		col1, col2, col3, col4 = st.columns(4)
		refresh_time = refresh_time.split(' ')[1]

		col1.write(f"{refresh_time} (UTC)")
		col1.metric(label="Current value", 
					value=str(current_value), 
					delta=(str(round((current_value - old_value),2)) + " ( "+ str(round((current_value - old_value)/old_value*100,2))+'% )')
					)
		col2.write(str(forecast_date_5m).split(' ')[1][0:5]+ " (UTC)")
		col2.metric(label = "Forecast 5 min", 
					value = str(round(new_5m,2)), 
					delta = str(round((new_5m - current_value),2)) +" ( "+str(round(((new_5m-current_value)/current_value*100),2))+"% )")
		col3.write(str(forecast_date_1h).split(' ')[1][0:5]+ " (UTC)")
		col3.metric(label = "Forecast 1 hour", 
					value = str(round(new_1h,2)), 
					delta = str(round((new_1h - current_value),2)) +" ( "+str(round(((new_1h - current_value)/current_value*100),2))+"% )")
		col4.write(str(forecast_date_1d).split(" ")[0])
		col4.metric(label = "Forecast 1 day", 
					value = str(round(new_1d,2)), 
					delta = str(round((new_1d - current_value),2)) +" ( "+str(round(((new_1d- current_value)/current_value*100),2))+"% )")


		old_value = current_value
#		round(stock.fast_info.last_price,2)

		c = alt.Chart(df_historic_1m[['date', 'hour (UTC)','close']]).mark_area(
			color="lightblue",
#			interpolate='step-after',
			line=True
			).encode(
			x=alt.X('hour (UTC)').title('hour (UTC)'),
			y=alt.Y('close:Q').title("USD").scale(domain=(min_value*0.999, max_value*1.001), clamp=True)).interactive()
		st.altair_chart(c, use_container_width=True)

		df_historic_1m.sort_values(by=['date'], ascending=False, inplace=True)

		st.dataframe(df_historic_1m[['day', 'hour (UTC)', 'open', 'high', 'low', 'close','volume']], hide_index=True)


next_month=(datetime.now().replace(day=1)+timedelta(days=32)) #.replace(day=1)+timedelta(days=-1)
st.title("Crude Oil "+next_month.strftime("%B")+" "+symbol)

placeholder = st.empty()

try:
	df_historic = pd.read_csv("./data/yf_data_1m.csv")
	old_value = df_historic['close'].tolist()[-1]
except Exception as e:
	old_value = 0
	print(e)

# Auto-refreshing loop
while True:
	update_dashboard()
	time.sleep(60)
