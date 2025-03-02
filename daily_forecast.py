import pandas as pd
import time
from datetime import datetime, timedelta
from datetime import timezone 
from pytz import timezone as tz

#import ta
#from ta.utils import dropna

#import yfinance as yf

#from sklearn.linear_model import LinearRegression
#from sklearn.model_selection import train_test_split
#from sklearn.metrics import mean_squared_error, r2_score

#from pycaret.regression import *

import pickle

import utils


lag_range_day = 7
lag_range_hour = 24*6
lag_range_min = 12*12 # 3

lag_day = 365*2
lag_hour = 24*60
lag_min = 12*24*7

symbol = 'CL=F'




def main():

	print('1 Day Forecast')
	df = utils.read_data(symbol, "max", "1d")
#	df = df[-720:]
	df_ta = utils.ta_index(df[-720:])
	df_ta = df.copy()

	best_model = utils.pycaret_model(df_ta, 'close', '1d')

	try:
		df_history = pd.read_csv("./data/yf_data_1d.csv")
		df_history['date'] = pd.to_datetime(df_history['date'], format='%Y-%m-%d')
	except:
		print("Missing History data")

	try:
		df_forecast = pd.read_csv("./data/forecast_1d.csv")
		df_forecast['date'] = pd.to_datetime(df_forecast['date'], format='%Y-%m-%d')
	except:
		df_forecast = pd.DataFrame()


	df_history = pd.concat([df_history, df_forecast])
	df_history.drop_duplicates(subset='date', inplace=True)

	forecast = utils.apply_model(df_history, 'close', "1d")

	forecast['date'] = pd.to_datetime(forecast['date'], format='%Y-%m-%d')

	if (forecast.shape[0]!=0):
		forecast.reset_index(inplace=True)
		forecast = pd.concat([df_forecast, forecast])
		forecast.drop_duplicates(subset='date', inplace=True)
		forecast[['date', 'close']].to_csv("./data/forecast_1d.csv", index=False)

	print("------------------------")
	print(forecast.head())
	print(forecast.info())
	print(forecast.tail())
	print("=======================================================")

	print('1 Hour Forecast')
	df = utils.read_data(symbol, "max", "1h")
#	df = df[-720*24:]
#	df_ta = ta_index(df)
	df_ta = utils.ta_index(df[-720*24:])
	df_ta = df.copy()

	best_model = utils.pycaret_model(df_ta, 'close', '1h')

	try:
		df_history = pd.read_csv("./data/yf_data_1h.csv")
		df_history['date'] = pd.to_datetime(df_history['date'], format='%Y-%m-%d %H:%M:%S')
	except:
		print("Missing History data")

	try:
		df_forecast = pd.read_csv("./data/forecast_1h.csv")
		df_forecast['date'] = pd.to_datetime(df_forecast['date'], format='%Y-%m-%d %H:%M:%S')
	except:
		df_forecast = pd.DataFrame()


	df_history = pd.concat([df_history, df_forecast])
	df_history.drop_duplicates(subset='date', inplace=True)

	forecast = utils.apply_model(df_history, 'close', "1h")

	forecast['date'] = pd.to_datetime(forecast['date'], format='%Y-%m-%d %H:%M:%S')

	if (forecast.shape[0]!=0):
		forecast.reset_index(inplace=True)
		forecast = pd.concat([df_forecast, forecast])
		forecast.drop_duplicates(subset='date', inplace=True)
		forecast[['date', 'close']].to_csv("./data/forecast_1h.csv", index=False)

	print("------------------------")
	print(forecast.head())
	print(forecast.info())
	print(forecast.tail())

	print("=======================================================")

	print('5 Minutes Forecast')

	df = utils.read_data(symbol, "max", "5m")
#	df = df[-720*24*60:]
#	df_ta = ta_index(df)
	df_ta = utils.ta_index(df[-12*24*59:])
	df_ta = df.copy()

	best_model = utils.pycaret_model(df_ta, 'close', '5m')

	try:
		df_history = pd.read_csv("./data/yf_data_1h.csv")
		df_history['date'] = pd.to_datetime(df_history['date'], format='%Y-%m-%d %H:%M:%S')
	except:
		print("Missing History data")

	try:
		df_forecast = pd.read_csv("./data/forecast_5m.csv")
		df_forecast['date'] = pd.to_datetime(df_forecast['date'], format='%Y-%m-%d %H:%M:%S')
	except:
		df_forecast = pd.DataFrame()



	df_history = pd.concat([df_history, df_forecast])
	df_history.drop_duplicates(subset='date', inplace=True)

	forecast = utils.apply_model(df_history, 'close', "5m")

	forecast['date'] = pd.to_datetime(forecast['date'], format='%Y-%m-%d %H:%M:%S')

	if (forecast.shape[0]!=0):
		forecast.reset_index(inplace=True)
		forecast = pd.concat([df_forecast, forecast])
		forecast.drop_duplicates(subset='date', inplace=True)
		forecast[['date', 'close']].to_csv("./data/forecast_5m.csv", index=False)

	print("------------------------")
	print(forecast.head())
	print(forecast.info())
	print(forecast.tail())

	print("=======================================================")


	return

if __name__ == '__main__':

	main()
