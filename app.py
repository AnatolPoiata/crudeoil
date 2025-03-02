#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Crude Oil Forecast project
#
# Basic interface on Streamlit
# 
#


#from RED.utils import *
#from RED.lib.common import _path
#from RED.lib.common import *
#from RED.lib.constants import *

#from RED.data import *

import datetime as dt
from datetime import datetime, date, timedelta


import pandas as pd
import numpy as np

import streamlit as st
from streamlit_extras.app_logo import add_logo


st.set_page_config(page_title='Oil price Forecasting', page_icon='📈', layout="centered", initial_sidebar_state="expanded", menu_items=None)

st.logo("./images/logo2.jpg")

#st.sidebar.image("./images/logo2.jpg", caption=None)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")


# Modele de prognozare
#_path.dashboard +

forecast = st.Page("./pages/stock_dashboard.py", title="Forecast",  default=True)
forecast_vs_fact = st.Page("./pages/forecast_vs_fact.py", title="Forecast vs Fact")
news = st.Page("./pages/news.py", title="News")

ta_ti =  st.Page("./pages/ta_details.py", title="Technical Indicators")
ta_ma =  st.Page("./pages/ta_ma.py", title="Moving Averages")


pg = st.navigation(
		{
	        "Forecast": [forecast],
            "Forecast vs Fact": [forecast_vs_fact],
            "News": [news],
            "Technical Analysis": [ta_ti, ta_ma]
        }
        )



def main():
    
    output_type=None
    output = pg.run()

if __name__ == "__main__":

	main()