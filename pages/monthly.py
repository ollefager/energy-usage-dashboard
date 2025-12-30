import streamlit as st

from pages.helper_functions import df_plot

st.header("Monthly Energy Usage")

hourly_data = st.session_state.hourly_data
daily_data = hourly_data.resample('d').sum()
monthly_data = hourly_data.resample('ME').sum()

monthly_data['load_price'] = monthly_data['total_cost'] / monthly_data['load_kwh']
monthly_data['heating_price'] = monthly_data['heating_cost'] / monthly_data['heating_kwh']
monthly_data['charging_price'] = monthly_data['charging_cost'] / monthly_data['charging_kwh']
monthly_data['base_load_price'] = monthly_data['base_cost'] / monthly_data['base_load_kwh']
monthly_data['other_price'] = monthly_data['other_cost'] / monthly_data['other_kwh']

plot_selection = st.pills(
    "Plot",
    options=['Cost', 'Consumption', 'Price', 'Solar gain', 'YoY'],
    selection_mode="single",
    default='Cost',
)

match plot_selection:
    case "Cost":
        df_plot(monthly_data, column_names=['total_cost', 'base_cost', 'heating_cost', 'charging_cost', 'other_cost'], y_label='SEK')
    case "Consumption":
        df_plot(monthly_data, column_names=['load_kwh', 'base_load_kwh', 'heating_kwh', 'charging_kwh', 'other_kwh'], y_label='kWh')
    case "Price":
        df_plot(monthly_data, column_names=['load_price', 'base_load_price', 'heating_price', 'charging_price', 'other_price'], y_label='SEK/kWh')
    case "Solar gain":
        df_plot(monthly_data, column_names=['pv_total_gain', 'pv_sold', 'pv_saved_cost'], y_label='SEK')
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
