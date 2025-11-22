import plotly.graph_objects as go
import streamlit as st


def df_plot(data, column_names):
    fig = go.Figure()

    for col_name in column_names:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[col_name],
            mode="lines+markers",
            name=col_name.replace("_", " ").title(),
            marker=dict(size=6),
            line=dict(width=2),
            hoverinfo='y',
        ))

    if st.session_state.device_type == 'phone':
        hover_mode = 'closest'
        legend = dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1)
        margin = dict(l=0, r=0, t=100, b=80)
    else:
        hover_mode = 'x unified'
        legend = dict(orientation="h")
        margin = dict(l=0, r=0, t=40, b=80)

    fig.update_layout(
        title="Cost",
        hovermode=hover_mode,
        legend=legend,
        margin=margin,
        height=500,
    )

    st.plotly_chart(fig, use_container_width=True)
