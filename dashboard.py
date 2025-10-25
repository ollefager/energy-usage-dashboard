import streamlit as st
import pandas as pd
st.title("Energy Usage Dashboard")

pv_data = pd.read_csv('electricityData/isolarcloud_hourly_data.csv',
                      na_values=["--"],
                      parse_dates=[0])
tibber_data = pd.read_csv('electricityData/tibber_data.csv',
                          parse_dates=[0, 1],
                          date_format='ISO8601')
ev_data = pd.read_csv('electricityData/zaptec_charging_data.csv')

iEnd = st.slider('end')
st.line_chart(pv_data['Load(W)'][:iEnd])

