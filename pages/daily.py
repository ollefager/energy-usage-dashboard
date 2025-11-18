import streamlit as st
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

st.header("Daily Energy Usage")

hourly_data = st.session_state.hourly_data
daily_data = hourly_data.resample('d').sum()
pv_data = st.session_state.pv_data

if 'slider_min' not in st.session_state:
    st.session_state.slider_min = daily_data.index.to_pydatetime()[0]
if 'slider_max' not in st.session_state:
    st.session_state.slider_max = daily_data.index.to_pydatetime()[-1]
if 'slider_val' not in st.session_state:
    st.session_state.slider_val = [st.session_state.slider_min, st.session_state.slider_max]

reset_interval = st.button('Reset interval')

[start_time, end_time] = st.slider(label='Time interval',
                                   key='slider_daily',
                                   min_value=st.session_state.slider_min,
                                   max_value=st.session_state.slider_max,
                                   value=st.session_state.slider_val)

if reset_interval:
    del st.session_state["slider_min"]
    del st.session_state["slider_max"]
    del st.session_state["slider_val"]
    st.rerun()

if start_time > st.session_state.slider_min:
    st.session_state.slider_min = start_time
    st.session_state.slider_val[0] = start_time
    st.rerun()

if end_time < st.session_state.slider_max:
    st.session_state.slider_max = end_time
    st.session_state.slider_val[1] = end_time
    st.rerun()

st.line_chart(daily_data[start_time:end_time], y=['heating_kwh', 'charging_kwh', 'base_load_kwh', 'load_kwh'])

if end_time - start_time < td(days=15):
    st.line_chart(pv_data[start_time:end_time], y=['load_w', 'base_load_w'])

st.line_chart(daily_data[start_time:end_time], y=['heating_cost', 'charging_cost', 'base_cost', 'total_cost', 'battery_charge_cost'])

st.line_chart(daily_data[start_time:end_time], y=['battery_charged_kwh', 'grid_bought_kwh', 'battery_charged_grid_kwh'])

st.line_chart(daily_data[start_time:end_time], y=['pv_sold'])

st.line_chart(daily_data[start_time:end_time], y=['load_diff_kwh'])
