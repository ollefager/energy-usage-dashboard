import streamlit as st
import plotly.graph_objects as go

st.header("Monthly Energy Usage")

hourly_data = st.session_state.hourly_data
daily_data = hourly_data.resample('d').sum()
monthly_data = hourly_data.resample('ME').sum()

# Assuming `monthly_data` is a DataFrame and has a DateTimeIndex or 'date' column
# If not, update accordingly
x = monthly_data.index if monthly_data.index.name else monthly_data['date']

fig = go.Figure()

# List of fields to plot
cost_fields = ['heating_cost', 'charging_cost', 'base_cost', 'total_cost', 'battery_charge_cost']

# Add each cost field as a line
for field in cost_fields:
    fig.add_trace(go.Scatter(
        x=x,
        y=monthly_data[field],
        mode="lines+markers",
        name=field.replace("_", " ").title(),
        marker=dict(size=6),
        line=dict(width=2),
        hoverinfo='y',
    ))

# Make it mobile-friendly
fig.update_layout(
    title="Cost",
    hovermode="closest",
    legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1),
    margin=dict(l=0, r=0, t=40, b=80),
    height=500,
)

st.plotly_chart(fig, use_container_width=True)

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