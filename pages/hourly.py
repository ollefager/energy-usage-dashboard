import streamlit as st
from datetime import datetime as dt
from datetime import timedelta

from pages.helper_functions import df_plot

st.header("Hourly Energy Usage")

hourly_data = st.session_state.hourly_data


earliest_time = hourly_data.index.to_pydatetime()[0]
latest_time = hourly_data.index.to_pydatetime()[-1]

max_hours = timedelta(hours=st.session_state.max_datapoints)

plot_selection = st.pills(
    "Plot",
    options=['Cost', 'Consumption', 'Solar gain'],
    selection_mode="single",
    default='Cost',
)

reset_interval = st.button('Reset interval')

start_date = st.date_input(label='Start date',
                           value=(latest_time - max_hours).date(),
                           min_value=earliest_time.date(),
                           max_value=latest_time.date())

if 'start_date_hourly' not in st.session_state or st.session_state.start_date_hourly != start_date:
    start_date_time = dt.combine(start_date, dt.min.time())
    st.session_state.slider_min_hourly = start_date_time
    st.session_state.start_date_hourly = start_date
    st.session_state.slider_max_hourly = min(latest_time, start_date_time + max_hours)

st.session_state.slider_val_hourly = [st.session_state.slider_min_hourly, st.session_state.slider_max_hourly]

[start_time, end_time] = st.slider(label='Time interval',
                                   key='slider_hourly',
                                   min_value=st.session_state.slider_min_hourly,
                                   max_value=st.session_state.slider_max_hourly,
                                   value=st.session_state.slider_val_hourly)

if reset_interval:
    del st.session_state["slider_min_hourly"]
    del st.session_state["slider_max_hourly"]
    del st.session_state["slider_val_hourly"]
    del st.session_state["start_date_hourly"]
    st.rerun()

if start_time > st.session_state.slider_min_hourly:
    st.session_state.slider_min_hourly = start_time
    st.session_state.slider_val_hourly[0] = start_time
    st.rerun()

if end_time < st.session_state.slider_max_hourly:
    st.session_state.slider_max_hourly = end_time
    st.session_state.slider_val_hourly[1] = end_time
    st.rerun()

match plot_selection:
    case "Cost":
        df_plot(hourly_data[start_time:end_time],
                column_names=['total_cost', 'base_cost', 'heating_cost', 'charging_cost', 'other_cost'], y_label='SEK')
    case "Consumption":
        df_plot(hourly_data[start_time:end_time],
                column_names=['load_kwh', 'base_load_kwh', 'heating_kwh', 'charging_kwh', 'other_kwh'], y_label='kWh')
    case "Solar gain":
        df_plot(hourly_data[start_time:end_time], column_names=['pv_total_gain', 'pv_sold', 'pv_saved_cost'],
                y_label='SEK')
