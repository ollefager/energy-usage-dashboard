import plotly.graph_objects as go
import streamlit as st


def df_plot(data, column_names=None, title=None, y_label=None, key='df_plot', y_range=[None,None]):
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
        fig.update_layout(yaxis=dict(title=dict(text=y_label),
                                     range=y_range))

    st.plotly_chart(fig, width='stretch', key=key)

import pandas as pd

def simulate_night_charging_reallocate(hourly_df,
                                       target_start_hour: int,
                                       target_end_hour: int,
                                       night_start: int = 0,
                                       night_end: int = 6,
                                       kwh_col: str = 'ev_charging_kwh',
                                       price_series: pd.Series | None = None):
    """
    Simulate reallocating the kWh charged during the night window (night_start..night_end-1)
    into a predefined target window (target_start_hour..target_end_hour-1) for each day.

    Args:
    - hourly_df: DataFrame indexed by Timestamp with hourly granularity.
    - target_start_hour,target_end_hour: ints 0-23 defining the target window. If start > end,
      the window wraps midnight.
    - night_start, night_end: ints defining the night window (end is exclusive).
    - kwh_col: column with actual EV kWh charged per hour to consider.
    - price_series: optional Series indexed like hourly_df containing price (SEK/kWh).
      If None, function will try to derive hourly price from
      `hourly_df['charging_cost']/hourly_df['charging_kwh']` or
      `hourly_df['total_cost']/hourly_df['load_kwh']`.

    Returns:
    - daily_summary: DataFrame indexed by date with columns:
        'night_kwh', 'original_night_cost', 'simulated_cost', 'cost_diff', 'pct_change'
    - hourly_simulated: copy of hourly_df with two added columns:
        'sim_ev_charging_kwh' and 'sim_ev_charging_cost' (the reallocated schedule)
    """
    df = hourly_df.copy()

    # Build price_series if not provided
    if price_series is None:
        price_series = pd.Series(index=df.index, dtype=float)
        if 'charging_kwh' in df.columns and 'charging_cost' in df.columns:
            mask = df['charging_kwh'] > 0
            price_series.loc[mask] = df.loc[mask, 'charging_cost'] / df.loc[mask, 'charging_kwh']
        if price_series.isna().all() and 'load_kwh' in df.columns and 'total_cost' in df.columns:
            mask2 = df['load_kwh'] > 0
            price_series.loc[mask2] = df.loc[mask2, 'total_cost'] / df.loc[mask2, 'load_kwh']

    # final check
    if price_series.isna().any():
        price_series = price_series.fillna(method='ffill').fillna(method='bfill')

    # helper to get hour list for a window (end exclusive)
    def hours_in_window(start, end):
        if start == end:
            return list(range(24))
        if start < end:
            return list(range(start, end))
        else:
            return list(range(start, 24)) + list(range(0, end))

    night_hours = set(hours_in_window(night_start, night_end))
    target_hours = hours_in_window(target_start_hour, target_end_hour)
    n_target = len(target_hours)
    if n_target == 0:
        raise ValueError("Target window contains no hours")

    # prepare output
    daily_rows = []
    sim_ev_kwh = pd.Series(0.0, index=df.index)
    sim_ev_cost = pd.Series(0.0, index=df.index)

    # iterate by calendar day (use local date from index)
    dates = pd.to_datetime(df.index).normalize().unique()
    for day in dates:
        day_mask = df.index.normalize() == day
        day_slice = df.loc[day_mask]
        if day_slice.empty:
            continue

        # night timestamps are those within the row's day that have hour in night_hours
        night_mask = day_slice.index.hour.isin(list(night_hours))
        night_kwh = float(day_slice.loc[night_mask, kwh_col].sum()) if kwh_col in day_slice.columns else 0.0

        # original cost during night (prefer 'charging_cost' if present)
        if 'charging_cost' in day_slice.columns:
            original_night_cost = float(day_slice.loc[night_mask, 'charging_cost'].sum())
        else:
            # fallback: multiply by price_series where available
            original_night_cost = float((day_slice.loc[night_mask, kwh_col] * price_series.loc[day_slice.loc[night_mask].index]).sum())

        # allocate equally into the target hours for that day
        # build target timestamps for that day (if hour < start and window wraps, those belong to next day)
        target_timestamps = []
        for h in target_hours:
            # determine timestamp that belongs to this day for hour h:
            ts = pd.Timestamp(day) + pd.Timedelta(hours=h)
            # if hour < night_start and target window wrapped into next day, ts already correct
            # but if target window includes hours that logically belong to next calendar day (e.g., target 22-06),
            # hours 0..5 belong to the same calendar day and hours 22..23 belong to the same day as ts above.
            # This simple construction is consistent (ts is that day's hour h).
            if ts in df.index:
                target_timestamps.append(ts)
            else:
                # try next day timestamp (in case target hour belongs to next day in index)
                ts_next = ts + pd.Timedelta(days=1)
                if ts_next in df.index:
                    target_timestamps.append(ts_next)

        # if we couldn't map target timestamps (missing data), skip day
        if len(target_timestamps) == 0:
            simulated_cost = 0.0
        else:
            per_hour_kwh = night_kwh / len(target_timestamps) if night_kwh != 0 else 0.0
            simulated_cost = 0.0
            for ts in target_timestamps:
                price = float(price_series.loc[ts])
                simulated_cost += price * per_hour_kwh
                sim_ev_kwh.loc[ts] += per_hour_kwh
                sim_ev_cost.loc[ts] += price * per_hour_kwh

        daily_rows.append({
            'date': day.date(),
            'night_kwh': night_kwh,
            'original_night_cost': original_night_cost,
            'simulated_cost': simulated_cost,
            'cost_diff': simulated_cost - original_night_cost,
            'pct_change': (simulated_cost - original_night_cost) / original_night_cost * 100 if original_night_cost != 0 else None
        })

    daily_summary = pd.DataFrame(daily_rows).set_index('date')
    hourly_simulated = df.copy()
    hourly_simulated['sim_charging_kwh'] = sim_ev_kwh
    hourly_simulated['sim_charging_cost'] = sim_ev_cost

    return daily_summary, hourly_simulated    
