import streamlit as st
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import requests
import io
import pickle

from helper_functions import *

st.title("Energy Usage Dashboard")

github_token = st.secrets["github_token"]
data_storage_url = "https://api.github.com/repos/ollefager/data-storage/contents/pv_data.pkl?ref=main"

headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.v3.raw"
}

if 'pv_data' not in st.session_state:
    pv_data_bytes = io.BytesIO(requests.get(data_storage_url + '/pv_data.pkl?ref=main', headers=headers).content)
    st.session_state.pv_data = pd.read_pickle(pv_data_bytes)
pv_data = st.session_state.pv_data

if 'ev_data' not in st.session_state:
    ev_data_bytes = io.BytesIO(requests.get(data_storage_url + '/ev_data.pkl?ref=main', headers=headers).content)
    st.session_state.ev_data = pd.read_pickle(ev_data_bytes)
ev_data = st.session_state.ev_data

if 'tibber_data' not in st.session_state:
    tibber_data_bytes = io.BytesIO(requests.get(data_storage_url + '/tibber_data.pkl?ref=main', headers=headers).content)
    st.session_state.tibber_data = pd.read_pickle(tibber_data_bytes)
tibber_data = st.session_state.tibber_data

if 'hourly_data' not in st.session_state:
    hourly_data_bytes = io.BytesIO(requests.get(data_storage_url + '/hourly_data.pkl?ref=main', headers=headers).content)
    st.session_state.hourly_data = pd.read_pickle(hourly_data_bytes)
hourly_data = st.session_state.hourly_data

pages = [st.Page("monthly_page.py", title="Monthly energy usage"),
         st.Page("daily_page.py", title="Daily energy usage"),
         st.Page("hourly_page.py", title="Hourly energy usage"),
         st.Page("five_min_page.py", title="5 min energy usage")]

pg = st.navigation(pages)
pg.run()
