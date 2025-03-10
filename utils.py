import pandas as pd
import time
from datetime import datetime, timedelta
from datetime import timezone 
from pytz import timezone as tz

import ta
from ta.utils import dropna

import yfinance as yf

#from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

from pycaret.regression import *

#import pickle
import warnings
warnings.filterwarnings("ignore") 


lag_range_day = 7
lag_range_hour = 24*6
lag_range_min = 12*12   #3

lag_day = 365*2
lag_hour = 24*30
lag_min = 12*24*7

symbol = 'CL=F'


def read_data(symbol, period, interval):

	try:
		df_old=pd.read_csv("./data/yf_data_"+interval+".csv")
	except:
		df_old=pd.DataFrame()



	if interval == '1m':
		period = '5d'
	elif interval == '5m':
		period = '1mo'
	elif interval == '1h':
		period = '2y'
	else:
		period = 'max'


	try:

		df = yf.download(symbol, period=period, interval=interval)
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

#		df.reset_index(inplace=True)

		df = pd.concat([df_old, df])

		df.drop_duplicates(subset=['date'],inplace=True)

		df[['date','open', 'high', 'low', 'close','volume']].to_csv("./data/yf_data_"+interval+".csv", index=False)

	except Exception as e:
		print(e)
		print('Cannot read dayta for yfinance')

		df=pd.read_csv("./data/yf_data_"+interval+".csv")

	return df[['date','open', 'high', 'low', 'close','volume']]

def ta_index(df):
	# Clean nan values
	df = ta.utils.dropna(df)
	# Add all ta features filling nans values
	df = ta.add_all_ta_features(
		df, "open", "high", "low", "close", "volume", fillna=True
		)
	return df

def pycaret_model(df, tr='close', interval="1d"):

	data = df[['date', tr]].copy()
#     data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d').dt.date
	data.set_index('date', inplace=True)

	if (interval=='1d'):
		lag_range = lag_range_day
		data_lag = lag_day
	elif (interval=='1h'):
		lag_range = lag_range_hour
		data_lag = lag_hour
	else:
		lag_range = lag_range_min
		data_lag = lag_min

	for lag in range(1, lag_range+1):
		data[f'Lag_{lag}'] = data[tr].shift(lag)

	data_lagged = data.dropna()
	data_lagged = data_lagged.tail(data_lag)

	historic_data = data_lagged
	historic_data.reset_index(drop=True, inplace=True)

	s = setup(data = historic_data, target = tr, train_size = 0.8, session_id=123, numeric_imputation='knn')

#	   normalize = True, normalize_method = 'zscore',

	best = compare_models(sort='MAPE', cross_validation=True)
	print('Best:',best)

#	plot_model(best, plot='feature')

#	model = create_model(best)


	print('----------------------------------------------------- et --------------------------------------------------')
	et = create_model('et', cross_validation=False)
	tuned_et = tune_model(et, optimize='MAPE')

	print('----------------------------------------------------- omp --------------------------------------------------')
	omp =  create_model('omp', cross_validation=False)
	tuned_omp = tune_model(omp, optimize='MAPE')

	print('----------------------------------------------------- huber --------------------------------------------------')

	huber = create_model('huber', cross_validation=False)
	tuned_huber = tune_model(huber, optimize='MAPE')

	print('----------------------------------------------------- blend --------------------------------------------------')

	blender = blend_models([tuned_et, tuned_omp,  tuned_huber], optimize='MAPE')

	print('----------------------------------------------------- top model --------------------------------------------------')

	top_model = compare_models(include=[tuned_et, tuned_omp, tuned_huber, blender], cross_validation=False)

	model = finalize_model(top_model)

	model_file = "model_"+interval

	save_model(model,model_file)

	return best

def apply_model(df, tr, interval, last_moment=None):

#	model = pickle.load(open("./models/model_"+interval+'.pkl', 'rb'))
	model = load_model("model_"+interval)

	df['date'] = df['date'].apply(lambda x: str(x).split("+")[0])

#	try:
#		df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S', utc=True)  
#	except:
#		try:
#			df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', utc=True)  
#		except:
	df['date'] = pd.to_datetime(df['date'], format='mixed', infer_datetime_format=True)


	try:
		last_time = df['date'].tolist()[-1]   #
	except Exception as e:
		print(e)
		print(df.info())
		print(df.head())
		print(df.tail())
		print(df.isnull().sum())
		input('Error in apply model')


	last_time = str(last_time).split("+")[0]

	if (last_moment):
		actual_time = last_moment.replace(tzinfo=timezone.utc)
		actual_time = actual_time+timedelta(days = 1)+timedelta(minutes = -1)
	else:
		actual_time = datetime.now(timezone.utc) 

	print('last_time:',last_time)
	print('actual_time:', actual_time)

	if (interval=="5m"):
		time_threshold = 5
		lag_range = lag_range_min
		data_lag = lag_min
		data_format = '%Y-%m-%d %H:%M:%S'
	elif (interval=="1h"):
		time_threshold = 60
		lag_range = lag_range_hour
		data_lag = lag_hour
		data_format = '%Y-%m-%d %H:%M:%S'
	else:
		time_threshold = 60*24
		lag_range = lag_range_day
		data_lag = lag_day
		data_format = '%Y-%m-%d'

	last_time = datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz('UTC'))

	df_prediction=pd.DataFrame()

	while (last_time<=actual_time):

		current_date = last_time + timedelta(minutes=time_threshold)
		df_temp = pd.DataFrame([{'date': current_date}])

		df_temp['date'] = pd.to_datetime(df_temp['date'], utc=True, format='mixed')   # data_format

		data = df[-lag_range-1:][[tr]].copy()

		for lag in range(1, lag_range+1):
			data[f'Lag_{lag}'] = data[tr].shift(lag)

#			df_lag = df[['date', tr]][-lag_range*2:].copy()
#			df_lag['date'] = pd.to_datetime(df_lag['date'], utc=True, format=data_format)
			
#		if (interval=="5m"):
		data = data[-1:]
		data['date'] = current_date
#			elif (interval=="1h"):
#				df_lag['date'] = df_lag['date'] + pd.Timedelta(hours=l)
#			else :
#				df_lag['date'] = df_lag['date'] + pd.Timedelta(days=l)

#			df_lag.rename(columns={tr:('Lag_'+str(l))}, inplace=True)
#			df_lag['date'] = pd.to_datetime(df_lag['date'], utc=True, format=data_format)

#			df_temp=pd.merge(df_temp, df_lag, on='date', how='left')

#		df_temp.drop_duplicates(subset='date', inplace=True)
#		df_temp.reset_index(inplace=True)

		X_forecast = data.drop(columns='date').copy()
		X_forecast.reset_index(inplace=True, drop=True)

		prediction = predict_model(model, data=X_forecast)

		print(current_date,'   prediction:', prediction['prediction_label'][0])

		data[tr] = prediction['prediction_label'][0]

		df = pd.concat([df, data[['date', tr]]])

		df_prediction = pd.concat([df_prediction, data[['date', tr]]])

		last_time = current_date

	return df_prediction