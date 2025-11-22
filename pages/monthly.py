import streamlit as st

from pages.helper_functions import df_plot

st.header("Monthly Energy Usage")

hourly_data = st.session_state.hourly_data
daily_data = hourly_data.resample('d').sum()
monthly_data = hourly_data.resample('ME').sum()

plot_selection = st.pills(
    "Plot",
    options=['Cost', 'Solar gain', 'YoY'],
    selection_mode="single",
    default='Cost',
)

match plot_selection:
    case "Cost":
        df_plot(monthly_data, ['heating_cost', 'charging_cost', 'base_cost', 'total_cost'], y_label='SEK')
    case "Solar gain":
        df_plot(monthly_data, ['pv_total_gain', 'pv_sold', 'pv_saved_cost'], y_label='SEK')
    case "YoY":
        option = st.selectbox('Data', monthly_data.columns, index=1, label_visibility='collapsed')

        if 'kwh' in option:
            y_label = 'kWh'
        elif 'w' in option:
            y_label = 'W'
        elif 'kw' in option:
            y_label = 'kW'
        elif 'soc' in option:
            y_label = '%'
        elif 'cost' in option:
            y_label = 'SEK'
        else:
            y_label = '-'


        monthly_data['year'] = monthly_data.index.year
        monthly_data['month'] = monthly_data.index.normalize().strftime("%m")
        yearly_monthly_data = monthly_data.pivot(index='month', columns='year', values=option)
        df_plot(yearly_monthly_data, y_label=y_label)
