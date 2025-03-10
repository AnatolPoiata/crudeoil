#!/usr/bin/env python
# coding: utf-8

#import yfinance as yf
import pandas as pd

import time
from datetime import datetime, timedelta

import os
import streamlit as st
import altair as alt

from sklearn.metrics import mean_absolute_percentage_error, r2_score, mean_absolute_error

symbol="CL=F"


def read_data(tr, interval):

	try:
		df_history = pd.read_csv("./data/yf_data_"+interval+".csv")
	except:
		df_history =  utils.read_data(symbol, "max", interval)



	df_history['fact'] = df_history[tr]

	try:
		df_forecast = pd.read_csv("./data/forecast_"+interval+".csv")
	except:
		df_forecast = pd.DataFrame()

	df_forecast['forecast'] = df_forecast[tr].round(2)


	df_history['date'] = df_history['date'].apply(lambda x: str(x).split("+")[0])
	df_forecast['date'] = df_forecast['date'].apply(lambda x: str(x).split("+")[0])


	if (interval=="5m"):
		data_format = '%Y-%m-%d %H:%M:%S'
	elif (interval=="1h"):
		data_format = '%Y-%m-%d %H:%M:%S'
	else:
		df_history['date'] = df_history['date'].apply(lambda x: str(x).split(" ")[0])
		df_forecast['date'] = df_forecast['date'].apply(lambda x: str(x).split(" ")[0])
		data_format = '%Y-%m-%d'



#	df_history['date'] = pd.to_datetime(df_history['date'], format='ISO8601', utc=True)   
#	df_forecast['date'] = pd.to_datetime(df_forecast['date'], format='ISO8601', utc=True)   

	try:
		df_history['date'] = pd.to_datetime(df_history['date'], format=data_format, utc=True)
	except:
#		df_history['date'] = pd.to_datetime(df_history['date'], format="%Y-%m-%d %H:%M:%S", utc=True)

    	df_history['date'] = pd.to_datetime(df_history['date'], format="mixed", utc=True)



	try:
		df_forecast['date'] = pd.to_datetime(df_forecast['date'], format=data_format, utc=True)
	except:
#		df_forecast['date'] = pd.to_datetime(df_forecast['date'], format="%Y-%m-%d %H:%M:%S", utc=True)

    	df_forecast['date'] = pd.to_datetime(df_forecast['date'], format="mixed", utc=True)


	df_temp1 = pd.merge(df_history[['date', 'fact']], df_forecast[['date', 'forecast']], on='date', how='left')
	df_temp2 = pd.merge(df_history[['date', 'fact']], df_forecast[['date', 'forecast']], on='date', how='right')

	df_temp=pd.concat([df_temp1, df_temp2])



	if (interval=="5m"):
		data_format="%Y-%m-%d %H:%M"
	elif (interval=="1h"):
		data_format = "%Y-%m-%d %H"
	elif (interval=="1d"):
		data_format="%Y-%m-%d"
	else:
		data_format="%Y-%m-%d %H:%M:%S"

	df_temp['date'] = pd.to_datetime(df_temp['date'], format=data_format)

	df_temp.drop_duplicates(subset='date', inplace=True)
	df_temp.sort_values(by=['date'], ascending=False, inplace=True)

	df_temp['diff'] = df_temp['forecast']-df_temp['fact']
	df_temp['pct'] = (df_temp['diff']/df_temp['fact']*100).round(2)

	return df_temp[['date', 'fact', 'forecast', 'diff', 'pct']]


def update_dashboard():

	next_month=(datetime.now().replace(day=1)+timedelta(days=32)) #.replace(day=1)+timedelta(days=-1)
	st.title("Crude Oil "+next_month.strftime("%B")+" "+symbol)

	df_1d = read_data("close", "1d")
	df_1d['date'] = df_1d['date'].apply(lambda x: str(x).split(" ")[0])
	df_1d['date'] = pd.to_datetime(df_1d['date'], format="%Y-%m-%d")

	print('----------------- df_1d---------------')
	print(df_1d.tail(20))
	print(df_1d.head(20))


	df_1h = read_data("close", "1h")

	print('----------------- df_1h---------------')
	print(df_1h.tail(20))
	print(df_1h.head(20))


	df_5m = read_data("close", "5m")

	refresh_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	st.session_state["tabs"] = ["5 minutes", "1 hour", "1 day"]
	tabs = st.tabs(st.session_state["tabs"])


	with tabs[0]:

		tabs[0].subheader("Forecast vs Fact (5 minutes  interval)")

		df_m=df_5m[(df_5m['fact'].notnull()) & (df_5m['forecast'].notnull())][:576].copy()   # [-72:]

		df_m=df_5m[(df_5m['fact']>0) & (df_5m['forecast']>0)][:576].copy()   # [-72:]

		min_value = min(df_m['fact'].min(), df_m['forecast'].min())
		max_value = max(df_m['fact'].max(), df_m['forecast'].max())   

#		print('min_value:', min_value, 'max_value:', max_value)

		line1 = alt.Chart(df_m).mark_line(interpolate="basis").encode(
			x=alt.X('date:T').title('hour (UTC)'),
			y=alt.Y('fact:Q').title("USD").scale(domain=(min_value*0.999, max_value*1.001), clamp=True),
			color=alt.value("#0099")
			)

		line2 = alt.Chart(df_m).mark_line(interpolate="basis").encode(
			x=alt.X('date:T').title('hour (UTC)'),
			y=alt.Y('forecast:Q').title("USD").scale(domain=(min_value*0.999, max_value*1.001), clamp=True),
			color=alt.value("#ff0000")
			)

		c = alt.layer(line1, line2)

		st.altair_chart(c, use_container_width=True)

		mape = mean_absolute_percentage_error(df_5m[df_5m['fact'].notnull() & df_5m['forecast'].notnull()]['fact'], df_5m[df_5m['fact'].notnull() & df_5m['forecast'].notnull()]['forecast'])
		mae = mean_absolute_error(df_5m[df_5m['fact'].notnull() & df_5m['forecast'].notnull()]['fact'], df_5m[df_5m['fact'].notnull() & df_5m['forecast'].notnull()]['forecast'])
		r2 = r2_score(df_5m[df_5m['fact'].notnull() & df_5m['forecast'].notnull()]['fact'], df_5m[df_5m['fact'].notnull() & df_5m['forecast'].notnull()]['forecast'])

		col1, col2, col3 = st.columns(3)

		col1.write(f"### MAPE: " + str(round(mape*100,2))+" %")
		col2.write(f"### MAE: "+str(round(mae,2)))
		col3.write(f"### R2: "+str(round(r2,2)))

		df_m['date'] = df_m['date'].apply(lambda x: str(x).split("+")[0][0:16])


		st.dataframe(df_m, hide_index=True)

	tabs[1].subheader("Forecast vs Fact (1 hour interval)")

	with tabs[1]:

		df_h=df_1h[df_1h['fact'].notnull() & df_1h['forecast'].notnull()][:336].copy()	#df_1h[:72].copy()

		print('------------------- df_1h ------------------')
		print(df_1h.tail())
		print('df_h:', df_h.shape)

		min_value = min(df_h['fact'].min(), df_h['forecast'].min())  # min()
		max_value = max(df_h['fact'].max(), df_h['forecast'].max())  #max()   


		line1 = alt.Chart(df_h).mark_line(interpolate="basis").encode(
			x=alt.X('date:T').title('hour (UTC)'),
			y=alt.Y('fact:Q').title("USD").scale(domain=(min_value*0.999, max_value*1.001), clamp=True),
			color=alt.value("#0099")
			)

		line2 = alt.Chart(df_h).mark_line(interpolate="basis").encode(
			x=alt.X('date:T').title('hour (UTC)'),
			y=alt.Y('forecast:Q').title("USD").scale(domain=(min_value*0.999, max_value*1.001), clamp=True),
			color=alt.value("#ff0000")
			)

		c = alt.layer(line1, line2)

		st.altair_chart(c, use_container_width=True)

		mape_1h = mean_absolute_percentage_error(df_1h[df_1h['fact'].notnull() & df_1h['forecast'].notnull()]['fact'], df_1h[df_1h['fact'].notnull() & df_1h['forecast'].notnull()]['forecast'])
		mae_1h = mean_absolute_error(df_1h[df_1h['fact'].notnull() & df_1h['forecast'].notnull()]['fact'], df_1h[df_1h['fact'].notnull() & df_1h['forecast'].notnull()]['forecast'])
		r2 = r2_score(df_1h[df_1h['fact'].notnull() & df_1h['forecast'].notnull()]['fact'], df_1h[df_1h['fact'].notnull() & df_1h['forecast'].notnull()]['forecast'])

		col1, col2, col3 = st.columns(3)

		col1.write(f"### MAPE: " + str(round(mape_1h*100,2))+" %")
		col2.write(f"### MAE: "+str(round(mae_1h,2)))
		col3.write(f"### R2: "+str(round(r2,2)))

#		df_h['date'] = df_h['date'].apply(lambda x: str(x).split("+")[0][0:16])
		df_h['date'] = df_h['date'].apply(lambda x: str(x).split("+")[0][0:10])


		st.dataframe(df_h, hide_index=True)

	tabs[2].subheader("Forecast vs Fact (1 day interval)")

	with tabs[2]:

		df_d = df_1d[df_1d['fact'].notnull() & df_1d['forecast'].notnull()][:60].copy()

		min_value = min(df_d['fact'].min(), df_d['forecast'].min())  # min()
		max_value = max(df_d['fact'].max(), df_d['forecast'].max())  #max()   

		line1 = alt.Chart(df_d).mark_line(interpolate="basis").encode(
			x=alt.X('date:T').title('Date'),
			y=alt.Y('fact:Q').title("USD").scale(domain=(min_value*0.999, max_value*1.001), clamp=True),
			color=alt.value("#0099")
			)

		line2 = alt.Chart(df_d).mark_line(interpolate="basis").encode(
			x=alt.X('date:T').title('Date)'),
			y=alt.Y('forecast:Q').title("USD").scale(domain=(min_value*0.999, max_value*1.001), clamp=True),
			color=alt.value("#ff0000")
			)

		c = alt.layer(
					line1, line2
				)

		st.altair_chart(c, use_container_width=True)

		print(df_1d.head(20))

		mape_1d = mean_absolute_percentage_error(df_1d[df_1d['fact'].notnull() & df_1d['forecast'].notnull()]['fact'], df_1d[df_1d['fact'].notnull() & df_1d['forecast'].notnull()]['forecast'])
		mae_1d = mean_absolute_error(df_1d[df_1d['fact'].notnull() & df_1d['forecast'].notnull()]['fact'], df_1d[df_1d['fact'].notnull() & df_1d['forecast'].notnull()]['forecast'])
		r2 = r2_score(df_5m[df_5m['fact'].notnull() & df_5m['forecast'].notnull()]['fact'], df_5m[df_5m['fact'].notnull() & df_5m['forecast'].notnull()]['forecast'])

		col1, col2, col3 = st.columns(3)

		col1.write(f"### MAPE: " + str(round(mape_1d*100,2))+" %")
		col2.write(f"### MAE: "+str(round(mae_1d,2)))
		col3.write(f"### R2: "+str(round(r2,2)))


		df_d['date'] = df_d['date'].apply(lambda x: str(x).split(" ")[0])

		st.dataframe(df_d, hide_index=True)


# Streamlit setup

#placeholder = st.empty()

# Auto-refreshing loop
#while True:
#	update_dashboard()
#	time.sleep(60)


def main():
	
	output_type=None
#	while True:
#		update_dashboard()
#		time.sleep(60)

	output = update_dashboard()


#if __name__ == "__main__":
main()
