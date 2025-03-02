import pandas as pd
import time
from datetime import datetime, timedelta
from datetime import timezone 
from pytz import timezone as tz

import yfinance as yf

import pickle

import utils


lag_range_day = 7
lag_range_hour = 24*6
lag_range_min = 12*12   #3

lag_day = 365*2
lag_hour = 24*60
lag_min = 12*24*7

symbol = 'CL=F'

init_date = datetime.strptime("2024-01-01", '%Y-%m-%d')


def main():

	
	print('1 Day Forecast')
	df = utils.read_data(symbol, period="max", interval="1d")
#	df=df.reset_index()

	df['date'] = pd.to_datetime(df['date'], utc=True, format='%Y-%m-%d %H:%M:%S')   # data_format

	dr = (datetime.now()-init_date).days

	df_forecast = pd.DataFrame()

	tr = 'close'
	interval = '1d'

	for dd in range(-dr-1, 0):

		last_moment= init_date+timedelta(days=(dr+dd+1))

		df_ta = df[df['date']<(last_moment.replace(tzinfo=tz('UTC')))].copy()

		if (df_ta.shape[0]==0):
			continue

		best_model = utils.pycaret_model(df_ta, tr, interval)
		prediction = utils.apply_model(df_ta[['date', tr]], tr, interval, last_moment = last_moment)

		print('prediction=', prediction)

		df_forecast = pd.concat([df_forecast, prediction[['date', tr]]])

	df_forecast =  df_forecast.drop_duplicates(subset='date', keep='last')


	df_forecast['date'] = pd.to_datetime(df_forecast['date'], format='%Y-%m-%d')

	if (df_forecast.shape[0]!=0):
		df_forecast[['date', 'close']].to_csv("./data/forecast_1d.csv", index=False)

	print("------------------------")
	print(df_forecast.head())
	print(df_forecast.info())
	print(df_forecast.tail())
	print("=======================================================")

	print('1 Hour Forecast')

	df = utils.read_data(symbol, "max", "1h")
#	df=df.reset_index()

	df['date'] = pd.to_datetime(df['date'], utc=True, format='%Y-%m-%d %H:%M:%S')   # data_format

	interval = '1h'

	df_forecast = pd.DataFrame()

	for dd in range(-dr-1, 0):


		last_moment= init_date+timedelta(days=(dr+dd+1))

		df_ta = df[df['date']<(last_moment.replace(tzinfo=tz('UTC')))].copy()

		if (df_ta.shape[0]==0):
			continue

		best_model = utils.pycaret_model(df_ta, tr, interval)
		prediction = utils.apply_model(df_ta[['date', tr]], tr, interval, last_moment = last_moment)

		print('prediction=', prediction.tail(10))

		df_forecast = pd.concat([df_forecast, prediction[['date', tr]]])

	df_forecast =  df_forecast.drop_duplicates(subset='date', keep='last')


	df_forecast['date'] = pd.to_datetime(df_forecast['date'], format='%Y-%m-%d %H:%M:%S')

	if (df_forecast.shape[0]!=0):
		df_forecast[['date', 'close']].to_csv("./data/forecast_1h.csv", index=False)

	print("------------------------")
	print(df_forecast.head())
	print(df_forecast.info())
	print(df_forecast.tail())
	print("=======================================================")
	

	print('5 Minutes Forecast')

	df = utils.read_data(symbol, "max", "5m")

#	df=df.reset_index()

	df['date'] = pd.to_datetime(df['date'], utc=True, format='%Y-%m-%d %H:%M:%S')   # data_format

	predictions=[]

	interval = '5m'

	df_forecast = pd.DataFrame()

	for dd in range(-dr-1, -1):

		last_moment = init_date+timedelta(days=(dr+dd+1))

		df_ta = df[df['date']<(last_moment.replace(tzinfo=tz('UTC')))].copy()

		if (df_ta.shape[0]==0):
			continue

		best_model = utils.pycaret_model(df_ta, tr, interval)
		prediction = utils.apply_model(df_ta[['date', tr]], tr, interval, last_moment = last_moment)

		print('prediction=')
		print(prediction.head(10))
		print(prediction.tail(10))

		try:
			df_forecast = pd.concat([df_forecast, prediction[['date', tr]]])
		except:
			pass

	df_forecast =  df_forecast.drop_duplicates(subset='date', keep='last')


	df_forecast['date'] = pd.to_datetime(df_forecast['date'], format='%Y-%m-%d %H:%M:%S')


	if (df_forecast.shape[0]!=0):
		df_forecast[['date', 'close']].to_csv("./data/forecast_5m.csv", index=False)

	print("------------------------")
	print(df_forecast.head())
	print(df_forecast.info())
	print(df_forecast.tail())
	print("=======================================================")

	return

if __name__ == '__main__':

	main()
