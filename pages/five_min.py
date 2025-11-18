import streamlit as st
from datetime import datetime as dt
from datetime import timedelta

st.header("5 Min Energy Usage")

pv_data = st.session_state.pv_data

if 'compare_5min' not in st.session_state:
    st.session_state.compare_5min = False

def click_button():
    st.session_state.compare_5min = not st.session_state.compare_5min

st.button('Compare', on_click=click_button)

if st.session_state.compare_5min:
    n_col = 2
else:
    n_col = 1

columns = st.columns(n_col)

for i in range(n_col):
    with columns[i]:
        latest_time = pv_data.index[-1]
        [startDate, endDate] = st.date_input(label='Select Date Range', value=[latest_time-timedelta(days=2),latest_time], key='date_input' + str(i))

        [startTime, endTime] = st.slider(label='Time interval',
                                         key='slider' + str(i),
                                         min_value=dt(startDate.year, startDate.month, startDate.day),
                                         max_value=dt(endDate.year, endDate.month, endDate.day),
                                         value=[dt(startDate.year, startDate.month, startDate.day), dt(endDate.year, endDate.month, endDate.day)])

        st.line_chart(pv_data[startTime:endTime], y=['load_w', 'base_load_w'])
        st.line_chart(pv_data[startTime:endTime], y=['pv_w', 'battery_discharged_w', 'battery_charged_w', 'load_w', 'grid_bought_w'])
        st.line_chart(pv_data[startTime:endTime], y=['load_diff_kwh'])