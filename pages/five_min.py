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
    with st.container(horizontal=True, width='content'):
        st.button('Compare', on_click=click_button)
        comparison_type = st.selectbox('Select comparison type', ['Year', 'Free'], label_visibility='collapsed', key='comp_type')

if st.session_state.compare_5min:
    n_col = 2
    if comparison_type == 'Year':
        MONTH_DAYS = {
            "January": 31,
            "February": 29,
            "March": 31,
            "April": 30,
            "May": 31,
            "June": 30,
            "July": 31,
            "August": 31,
            "September": 30,
            "October": 31,
            "November": 30,
            "December": 31,
        }

        MONTHS = list(MONTH_DAYS.keys())

        # the structure below is needed to be able to update selectboxes based on button presses
        # and at the same time render the buttons after the selectboxes
        if "comp_dummy_date" not in st.session_state:
            st.session_state.comp_dummy_date = dt(2000, 1, 1)
            st.session_state.select_month = MONTHS[st.session_state.comp_dummy_date.month - 1]
            st.session_state.select_day = st.session_state.comp_dummy_date.day

        # use callbacks so buttons (rendered after selectboxes) can update them
        def _prev_day():
            st.session_state.comp_dummy_date -= timedelta(days=1)
            st.session_state.select_month = MONTHS[st.session_state.comp_dummy_date.month - 1]
            st.session_state.select_day = st.session_state.comp_dummy_date.day

        def _next_day():
            st.session_state.comp_dummy_date += timedelta(days=1)
            st.session_state.select_month = MONTHS[st.session_state.comp_dummy_date.month - 1]
            st.session_state.select_day = st.session_state.comp_dummy_date.day

        with st.container(horizontal=True, width='content', vertical_alignment='bottom'):
            selected_comp_month = st.selectbox("Select Month",
                                               list(MONTH_DAYS.keys()),
                                               key='select_month')
            selected_comp_day = st.selectbox("Select Day",
                                             list(range(1, MONTH_DAYS[selected_comp_month] + 1)),
                                             key='select_day')
            st.button("🡄", on_click=_prev_day, key='btn_prev_day')
            st.button("🡆", on_click=_next_day, key='btn_next_day')
            
            selected_comp_date = dt.strptime('-'.join(['2000', selected_comp_month, str(selected_comp_day)]), "%Y-%B-%d")
            if selected_comp_date != st.session_state.comp_dummy_date:
                st.session_state.comp_dummy_date = selected_comp_date              
else:
    n_col = 1

columns = st.columns(n_col)

if n_col == 1:
    comparison_type = 'Free'

for i in range(n_col):
    with columns[i]:
        show_full_range = False
        match comparison_type:
            case 'Free':
                with st.container(horizontal=True, width='content'):
                    reset_interval = st.button('Reset interval', key=f'reset_button_{i}')
                    if n_col == 1 and st.session_state.device_type == 'computer':
                        show_full_range = st.checkbox('Show full range', key='full_range_checkbox')

                if show_full_range:
                    start_date = earliest_time.date()
                    max_minutes = latest_time - earliest_time
                else:    
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
            case 'Year':

                comp_year = st.selectbox('Select year', [2025, 2024, 2023], label_visibility='collapsed', key=f'year_{i}')

                comp_date = st.session_state.comp_dummy_date.replace(year=comp_year)

                start_time = dt.combine(comp_date, dt.min.time())
                end_time = dt.combine(comp_date, dt.max.time())

        match plot_selection:
            case "Load":
                df_plot(pv_data[start_time:end_time], column_names=['load_w', 'base_load_w'], y_label='W', y_range=[0, 10000], key=f'5min_plot_{i}')        
