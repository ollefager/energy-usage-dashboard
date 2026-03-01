import streamlit as st
from datetime import timedelta

from pages.helper_functions import df_plot

st.header("Daily Energy Usage")

hourly_data = st.session_state.hourly_data
daily_data = hourly_data.resample('d').sum()
daily_data['hdd'] = (20 - hourly_data['out_temp']).clip(lower=0).resample('d').mean()
daily_data['price'] = hourly_data['price'].resample('d').mean()

earliest_date = daily_data.index.to_pydatetime()[0]
latest_date = daily_data.index.to_pydatetime()[-1]

max_days = timedelta(days=st.session_state.max_datapoints)

col_pills, col_toggle = st.columns([4, 1])

with col_pills:
    plot_selection = st.pills(
        "Plot",
        options=['Cost', 'Consumption', 'Solar gain'],
        selection_mode="single",
        default='Cost',
        label_visibility='collapsed',
    )

with col_toggle:
    show_temp_price = st.toggle("Temp & Price", value=False)

reset_interval = st.button('Reset interval')

if st.session_state.device_type == 'phone':
    start_date = st.date_input(label='Start date',
                               value=latest_date - max_days,
                               min_value=earliest_date,
                               max_value=latest_date)
        
    if 'start_date_daily' not in st.session_state or st.session_state.start_date_daily != start_date:
        st.session_state.slider_min_daily = start_date
        st.session_state.start_date_daily = start_date
        st.session_state.slider_max_daily = min(latest_date.date(), start_date + max_days)
else:
    if 'slider_min_daily' not in st.session_state:
        st.session_state.slider_min_daily = earliest_date
        st.session_state.slider_max_daily = latest_date

st.session_state.slider_val_daily = [st.session_state.slider_min_daily, st.session_state.slider_max_daily]

[start_time, end_time] = st.slider(label='Time interval',
                                   key='slider_daily',
                                   min_value=st.session_state.slider_min_daily,
                                   max_value=st.session_state.slider_max_daily,
                                   value=st.session_state.slider_val_daily)

if reset_interval:
    del st.session_state["slider_min_daily"]
    del st.session_state["slider_max_daily"]
    del st.session_state["slider_val_daily"]
    if 'start_date_daily' in st.session_state:
        del st.session_state["start_date_daily"]
    st.rerun()

if start_time > st.session_state.slider_min_daily:
    st.session_state.slider_min_daily = start_time
    st.session_state.slider_val_daily[0] = start_time
    st.rerun()

if end_time < st.session_state.slider_max_daily:
    st.session_state.slider_max_daily = end_time
    st.session_state.slider_val_daily[1] = end_time
    st.rerun()

match plot_selection:
    case "Cost":
        df_plot(daily_data[start_time:end_time], column_names=['total_cost', 'base_cost', 'heating_cost', 'charging_cost', 'other_cost'], y_label='SEK', add_temp_and_price=show_temp_price)
    case "Consumption":
        df_plot(daily_data[start_time:end_time], column_names=['load_kwh', 'base_load_kwh', 'heating_kwh', 'charging_kwh', 'other_kwh'], y_label='kWh', add_temp_and_price=show_temp_price)
    case "Solar gain":
        df_plot(daily_data[start_time:end_time], column_names=['pv_total_gain', 'pv_sold', 'pv_saved_cost'], y_label='SEK', add_temp_and_price=show_temp_price)