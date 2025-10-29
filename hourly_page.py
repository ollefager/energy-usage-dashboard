import streamlit as st
from datetime import datetime as dt
from datetime import timedelta

from five_min_page import latest_time

st.header("Hourly Energy Usage")

hourly_data = st.session_state.hourly_data

# get the latest time when all columns have data
latest_time = hourly_data.apply(lambda col: col[(col != 0) & (~col.isna())].index.max()).min()

[startDate, endDate] = st.date_input(label='Select Date Range', value=[latest_time-timedelta(days=2),latest_time])

[startTime, endTime] = st.slider(label='Time interval',
                                 min_value=dt(startDate.year, startDate.month, startDate.day),
                                 max_value=dt(endDate.year, endDate.month, endDate.day),
                                 value=[dt(startDate.year, startDate.month, startDate.day), dt(endDate.year, endDate.month, endDate.day)])

st.line_chart(hourly_data[startTime:endTime], y=['energy_kwh', 'load_kwh', 'base_load_kwh'])
st.line_chart(hourly_data[startTime:endTime], y='heating_kwh')
