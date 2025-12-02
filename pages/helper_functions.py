import plotly.graph_objects as go
import streamlit as st


def df_plot(data, column_names=None, title=None, y_label=None):
    fig = go.Figure()

    if column_names is None:
        column_names = data.columns

    if len(data.index) < 50:
        line_mode = 'lines+markers'
    else:
        line_mode = 'lines'

    for col_name in column_names:
        if col_name is str:
            legend_name = col_name.replace("_", " ").title()
        else:
            legend_name = str(col_name)

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data[col_name],
            mode=line_mode,
            name=legend_name,
            marker=dict(size=6),
            line=dict(width=2),
            hoverinfo='y+x',
        ))

    if st.session_state.device_type == 'phone':
        hover_mode = 'x'
        legend = dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1)
        margin = dict(l=0, r=0, t=100, b=80)
    else:
        hover_mode = 'x unified'
        legend = dict(orientation="h")
        margin = dict(l=0, r=0, t=0, b=80)

    fig.update_layout(
        hovermode=hover_mode,
        legend=legend,
        margin=margin,
        height=500
    )

    if title is not None:
        margin.t = 40
        fig.update_layout(title=title, margin=margin)

    if y_label is not None:
        fig.update_layout(yaxis=dict(title=dict(text=y_label)))

    st.plotly_chart(fig, use_container_width=True)
