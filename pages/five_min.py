import streamlit as st
from datetime import datetime as dt
from datetime import timedelta

from pages.helper_functions import df_plot


def click_button():
    st.session_state.compare_5min = not st.session_state.compare_5min


st.header("5 Min Energy Usage")

pv_data = st.session_state.pv_data

earliest_time = pv_data.index.to_pydatetime()[0]
latest_time = pv_data.index.to_pydatetime()[-1]

max_minutes = timedelta(minutes=max(st.session_state.max_datapoints * 5, 24*60))

plot_selection = st.pills(
    "Plot",
    options=['Load'],
    selection_mode="single",
    default='Load',
)

if 'compare_5min' not in st.session_state:
    st.session_state.compare_5min = False

if st.session_state.device_type == 'computer':
    st.button('Compare', on_click=click_button)

if st.session_state.compare_5min:
    n_col = 2
else:
    n_col = 1

columns = st.columns(n_col)

for i in range(n_col):
    with columns[i]:
        reset_interval = st.button('Reset interval', key=f'reset_button_{i}')

        start_date = st.date_input(label='Start date',
                                   key=f'date_input_{i}',
                                   value=(latest_time - max_minutes).date(),
                                   min_value=earliest_time.date(),
                                   max_value=latest_time.date())

        if f'start_date_5min_{i}' not in st.session_state or getattr(st.session_state, f'start_date_5min_{i}') != start_date:
            start_date_time = dt.combine(start_date, dt.min.time())
            setattr(st.session_state, f'slider_min_5min_{i}', start_date_time)
            setattr(st.session_state, f'start_date_5min_{i}', start_date)
            setattr(st.session_state, f'slider_max_5min_{i}', min(latest_time, start_date_time + max_minutes))

        slider_min = getattr(st.session_state, f'slider_min_5min_{i}')
        slider_max = getattr(st.session_state, f'slider_max_5min_{i}')
        setattr(st.session_state, f'slider_val_5min_{i}', [slider_min, slider_max])

        [start_time, end_time] = st.slider(label='Time interval',
                                           key=f'slider_{i}',
                                           min_value=slider_min,
                                           max_value=slider_max,
                                           value=getattr(st.session_state, f'slider_val_5min_{i}'),
                                           step=timedelta(minutes=5))

        if reset_interval:
            del st.session_state[f'slider_min_5min_{i}']
            del st.session_state[f'slider_max_5min_{i}']
            del st.session_state[f'slider_val_5min_{i}']
            del st.session_state[f'start_date_5min_{i}']
            st.rerun()

        if start_time > slider_min:
            setattr(st.session_state, f'slider_min_5min_{i}', start_time)
            slider_val = getattr(st.session_state, f'slider_val_5min_{i}')
            setattr(st.session_state, f'slider_val_5min_{i}', [start_time, slider_val[1]])
            st.rerun()

        if end_time < slider_max:
            setattr(st.session_state, f'slider_max_5min_{i}', end_time)
            slider_val = getattr(st.session_state, f'slider_val_5min_{i}')
            setattr(st.session_state, f'slider_val_5min_{i}', [slider_val[0], end_time])
            st.rerun()

        match plot_selection:
            case "Load":
                df_plot(pv_data[start_time:end_time],
                        column_names=['load_w', 'base_load_w'], y_label='W')
