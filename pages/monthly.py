import streamlit as st

from pages.helper_functions import line_plot

st.header("Monthly Energy Usage")

hourly_data = st.session_state.hourly_data
daily_data = hourly_data.resample('d').sum()
monthly_data = hourly_data.resample('ME').sum()

line_plot(monthly_data, ['heating_cost', 'charging_cost', 'base_cost', 'total_cost', 'battery_charge_cost'])

st.line_chart(monthly_data, y=['heating_cost', 'charging_cost', 'base_cost', 'total_cost', 'battery_charge_cost'])

st.line_chart(monthly_data, y=['grid_sold_kwh'])
st.line_chart(monthly_data, y=['pv_total_gain', 'pv_sold', 'pv_saved_cost'])
st.line_chart(monthly_data, y=['load_diff_kwh'])

monthly_data['year'] = monthly_data.index.year
monthly_data['month'] = monthly_data.index.normalize().strftime("%m")
yearly_monthly_data = monthly_data.pivot(index='month', columns='year', values='cost')
st.line_chart(yearly_monthly_data)
yearly_monthly_data = monthly_data.pivot(index='month', columns='year', values='consumption_kwh')
st.line_chart(yearly_monthly_data)
yearly_monthly_data = monthly_data.pivot(index='month', columns='year', values='charging_kwh')
st.line_chart(yearly_monthly_data)