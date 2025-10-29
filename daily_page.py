import streamlit as st

st.header("Daily Energy Usage")

hourly_data = st.session_state.hourly_data
daily_data = hourly_data.resample('d').sum()
st.line_chart(daily_data, y=['consumption_kwh'])
st.line_chart(daily_data, y=['heating_cost', 'charging_cost', 'base_cost'])
st.line_chart(daily_data, y=['heating_kwh', 'energy_kwh', 'base_load_kwh'])