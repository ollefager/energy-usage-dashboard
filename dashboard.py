import streamlit as st
from streamlit_js_eval import streamlit_js_eval

import pandas as pd
import requests
import io
import time


st.title("Energy Usage Dashboard")

github_token = st.secrets["github_token"]
data_storage_url = "https://api.github.com/repos/ollefager/data-storage/contents"

headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.v3.raw"
}

if 'pv_data' not in st.session_state:
    pv_data_bytes = io.BytesIO(requests.get(data_storage_url + '/pv_data.pkl?ref=main', headers=headers).content)
    st.session_state.pv_data = pd.read_pickle(pv_data_bytes)

if 'ev_data' not in st.session_state:
    ev_data_bytes = io.BytesIO(requests.get(data_storage_url + '/ev_data.pkl?ref=main', headers=headers).content)
    st.session_state.ev_data = pd.read_pickle(ev_data_bytes)

if 'tibber_data' not in st.session_state:
    tibber_data_bytes = io.BytesIO(requests.get(data_storage_url + '/tibber_data.pkl?ref=main', headers=headers).content)
    st.session_state.tibber_data = pd.read_pickle(tibber_data_bytes)

if 'hourly_data' not in st.session_state:
    hourly_data_bytes = io.BytesIO(requests.get(data_storage_url + '/hourly_data.pkl?ref=main', headers=headers).content)
    st.session_state.hourly_data = pd.read_pickle(hourly_data_bytes)

if 'device_type' not in st.session_state:
    user_agent = streamlit_js_eval(js_expressions="navigator.userAgent", key="ua")
    time.sleep(1)  # wait so that user_agent gets a value, should be after for some reason...
    user_agent = None

    if user_agent:
        user_agent = user_agent.lower()
        if any(keyword in user_agent.lower() for keyword in ['iphone', 'android', 'mobile']):
            st.session_state.device_type = 'phone'
            st.session_state.max_datapoints = 100
        else:
            st.session_state.device_type = 'computer'
            st.session_state.max_datapoints = 1000
    else:
        st.session_state.device_type = 'phone'
        st.session_state.max_datapoints = 100

pages = [st.Page("pages/home.py", title="Home"),
         st.Page("pages/monthly.py", title="Monthly energy usage"),
         st.Page("pages/daily.py", title="Daily energy usage"),
         st.Page("pages/hourly.py", title="Hourly energy usage"),
         st.Page("pages/five_min.py", title="5 min energy usage")]

pg = st.navigation(pages)
pg.run()
