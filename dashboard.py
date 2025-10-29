import streamlit as st
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta

from helper_functions import *

st.title("Energy Usage Dashboard")

if 'pv_data' not in st.session_state:
    st.session_state.pv_data = get_pv_data()
pv_data = st.session_state.pv_data

if 'ev_data' not in st.session_state:
    st.session_state.ev_data = get_ev_data()
ev_data = st.session_state.ev_data

if 'tibber_data' not in st.session_state:
    st.session_state.tibber_data = get_tibber_data()
tibber_data = st.session_state.tibber_data

if 'hourly_data' not in st.session_state:
    hourly_data = pd.concat([tibber_data, ev_data, pv_data.resample('h').sum()], axis=1)
    hourly_data['heating_kwh'] = hourly_data['load_kwh'] - hourly_data['base_load_kwh'] - hourly_data['energy_kwh']
    grid_price = 0.8
    hourly_data['heating_cost'] = hourly_data['heating_kwh'] * (hourly_data['price'] + grid_price)
    hourly_data['charging_cost'] = hourly_data['energy_kwh'] * (hourly_data['price'] + grid_price)
    hourly_data['base_cost'] = hourly_data['base_load_kwh'] * (hourly_data['price'] + grid_price)
    st.session_state.hourly_data = hourly_data
hourly_data = st.session_state.hourly_data

pages = [st.Page("daily_page.py", title="Daily energy usage"),
         st.Page("hourly_page.py", title="Hourly energy usage"),
         st.Page("five_min_page.py", title="5 min energy usage")]

pg = st.navigation(pages)
pg.run()

# monthly_data = hourly_data.resample('ME').sum()
# st.line_chart(monthly_data[monthly_data.index.year == 2025], y=['consumption', 'grid_bought', 'load'])
#
# monthly_data['year'] = monthly_data.index.year
# monthly_data['month'] = monthly_data.index.normalize().strftime("%m")
# yearly_monthly_data = monthly_data.pivot(index='month', columns='year', values='consumption')
# st.line_chart(yearly_monthly_data)
# yearly_monthly_data = monthly_data.pivot(index='month', columns='year', values='grid_bought')
# st.line_chart(yearly_monthly_data)
# yearly_monthly_data = monthly_data.pivot(index='month', columns='year', values='ev_charge')
# st.line_chart(yearly_monthly_data)
