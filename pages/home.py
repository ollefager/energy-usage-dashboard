import streamlit as st
import pandas as pd

hourly_data = st.session_state.hourly_data
daily_data = hourly_data.resample('d').sum()
monthly_mean = hourly_data.resample('d').mean()

last_update = st.session_state.hourly_data.index[-1]
data_up_to_date = pd.Timestamp.today().date() == last_update.date()

if data_up_to_date:
    text_color = 'green'
else:
    text_color = 'red'

st.markdown(f":{text_color}-badge[:material/check: Data up to date] :{text_color}-badge[Last update: {last_update}]")

st.subheader("Cost yesterday")

total_cost_yesterday = round(daily_data['total_cost'].iloc[-2])
better_than_monthly_avg = total_cost_yesterday <= monthly_mean['total_cost'].iloc[-1]

better_than_monthly_avg = False

if better_than_monthly_avg:
    bg_color = '#21522b'
    fg_color = '#8cd49b'
else:
    bg_color = '#750e23'
    fg_color = '#d9a09c'

st.markdown(f"""
<span style='
    background-color: {bg_color};
    color: {fg_color};
    font-size: 22px;
    padding: 8px 55px;
    border-radius: 20px;
    display: inline-block;
'>
    {total_cost_yesterday} kr
</span>
""", unsafe_allow_html=True)
