import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def get_pv_data():
    pv_data = pd.read_csv('electricityData/isolarcloud_hourly_data.csv',
                          na_values=["--"],
                          parse_dates=[0])

    # Check a problematic column
    problemColumn = 'Battery SOC(%)'

    # Strip whitespace
    pv_data[problemColumn] = pv_data[problemColumn].str.strip()

    # Optional: view unique values and types
    print(pv_data[problemColumn].apply(type).value_counts())
    print(pv_data[problemColumn].unique())

    # Convert to numeric
    pv_data[problemColumn] = pd.to_numeric(pv_data[problemColumn], errors='coerce')

    # Optionally drop NaNs if conversion failed
    pv_data = pv_data.dropna(subset=[problemColumn])

    # Now it's safe to convert to int
    pv_data[problemColumn] = pv_data[problemColumn].astype('int64')

    pv_data_new = pd.DataFrame()
    pv_data_new['time'] = pd.to_datetime(pv_data['Time'])
    pv_data_new['load_w'] = pv_data['Load(W)']
    pv_data_new['load_kwh'] = pv_data_new['load_w'] * (5 / 60) / 1000
    # pv_data_new['heating_w'] = pv_data['Load(W)']
    # pv_data_new['heating_w'][pv_data['Load(W)'].diff() < 2000] = None
    # pv_data_new['heating_w'].iloc[0] = None
    # pv_data_new['heating_w'] = pv_data_new['heating_w'].ffill()
    # pv_data_new['heating_w'][pv_data['Load(W)'] < 2000] = 0
    # pv_data_new['base_load_w'] = pv_data_new['load_w'] - pv_data_new['heating_w']
    pv_data_new['base_load_w'] = pv_data['Load(W)']
    pv_data_new.loc[pv_data['Load(W)'] >= 2000, 'base_load_w'] = None
    pv_data_new['base_load_w'] = pv_data_new['base_load_w'].ffill()
    pv_data_new['base_load_kwh'] = pv_data_new['base_load_w'] * (5 / 60) / 1000
    pv_data_new['battery_soc'] = pv_data['Battery SOC(%)']
    pv_data_new['grid_bought_w'] = pv_data['Grid(W)'].clip(lower=0)
    pv_data_new['grid_bought_kwh'] = pv_data_new['grid_bought_w'] * (5 / 60) / 1000
    pv_data_new['grid_sold_w'] = np.abs(pv_data['Grid(W)'].clip(upper=0))
    pv_data_new['grid_sold_kwh'] = pv_data_new['grid_sold_w'] * (5 / 60) / 1000
    pv_data_new['pv_w'] = pv_data['PV(W)']
    pv_data_new['pv_kwh'] = pv_data_new['pv_w'] * (5 / 60) / 1000
    pv_data_new['battery_discharged_w'] = pv_data['Battery(W)'].clip(lower=0)
    pv_data_new['battery_discharged_kwh'] = pv_data_new['battery_discharged_w'] * (5 / 60) / 1000
    pv_data_new['battery_charged_w'] = np.abs(pv_data['Battery(W)'].clip(upper=0))
    pv_data_new['battery_charged_kwh'] = pv_data_new['battery_charged_w'] * (5 / 60) / 1000
    pv_data_new['consumed_production_w'] = pv_data_new['pv_w'] + pv_data_new['battery_discharged_w'] - pv_data_new['grid_sold_w'] - pv_data_new['battery_charged_w']
    pv_data_new['consumed_production_kwh'] = pv_data_new['consumed_production_w'] * (5 / 60) / 1000
    pv_data_new['pv_excess_w'] = pv_data_new['pv_w'] - pv_data_new['load_w']
    pv_data_new['pv_excess_w'] = pv_data_new['pv_excess_w'].clip(lower=0)
    pv_data_new['battery_charged_grid_w'] = pv_data_new['pv_excess_w'] - pv_data_new['battery_charged_w']
    pv_data_new['battery_charged_grid_w'] = np.abs(pv_data_new['battery_charged_grid_w'].clip(upper=0))
    pv_data_new['battery_charged_grid_kwh'] = pv_data_new['battery_charged_grid_w'] * (5 / 60) / 1000
    pv_data_new['load_diff_w'] = pv_data_new['load_w'] - pv_data_new['pv_w'] - pv_data_new['battery_discharged_w'] - pv_data_new['grid_bought_w']
    pv_data_new['load_diff_kwh'] = pv_data_new['load_diff_w'] * (5 / 60) / 1000

    pv_data_new = pv_data_new.set_index('time')

    return pv_data_new

def get_tibber_data():
    tibber_data = pd.read_csv('electricityData/tibber_data.csv',
                              parse_dates=[0, 1],
                              date_format='ISO8601')

    tibber_data_new = pd.DataFrame()
    tibber_data_new['time'] = pd.to_datetime(tibber_data['From'], utc=True).dt.tz_convert('Europe/Stockholm').dt.tz_localize(None)
    tibber_data_new['price'] = tibber_data['Price per kWh']
    tibber_data_new['consumption_kwh'] = tibber_data['Consumption']
    tibber_data_new['cost'] = tibber_data['Cost']

    tibber_data_new = tibber_data_new.set_index('time')

    # remove duplicates
    tibber_data_new = tibber_data_new[~tibber_data_new.index.duplicated(keep="first")]

    return tibber_data_new

def get_ev_data():
    ev_data = pd.read_csv('electricityData/zaptec_charging_data.csv')

    # --- Clean and prepare ---
    ev_data["energy (kWh)"] = ev_data["energy (kWh)"].str.replace("kWh", "").astype(float)
    ev_data["charging power (kW)"] = ev_data["charging power (kW)"].str.replace("kW", "").astype(float)

    # Extract start time (e.g. "23:00" from "23:00 - 00:00")
    ev_data["hour_start"] = ev_data["time"].str.split(" - ").str[0]
    ev_data["hour_end"] = ev_data["time"].str.split(" - ").str[1]

    # Parse session start and end datetimes
    ev_data["started"] = pd.to_datetime(ev_data["started"], format="%d %b %Y, %H:%M")
    ev_data["ended"] = pd.to_datetime(ev_data["ended"], format="%d %b %Y, %H:%M")

    # --- Function to assign correct datetimes within a session ---
    def expand_session(session_df):
        timestamps = []
        energy_per_hour = []
        current_day = session_df["started"].iloc[0].normalize()
        prev_hour = -1

        for i in range(session_df.shape[0]):
            hour_start_str = session_df['hour_start'].iloc[i]
            hour_end_str = session_df['hour_end'].iloc[i]
            hour = int(hour_start_str.split(":")[0])
            if hour < prev_hour:  # time wrapped around → new day
                current_day += pd.Timedelta(days=1)
            hour_start = pd.to_datetime(f"{current_day.date()} {hour_start_str}")
            hour_end = pd.to_datetime(f"{current_day.date()} {hour_end_str}")
            minutes_in_hour = (hour_end - hour_start).seconds / 60
            energy_per_hour.append((minutes_in_hour/60) * session_df["charging power (kW)"].iloc[i])
            ts = pd.to_datetime(f"{current_day.date()} {hour}:00")
            timestamps.append(ts)
            prev_hour = hour

        session_df_new = pd.DataFrame()
        session_df_new["time"] = timestamps
        session_df_new["charging_kwh"] = energy_per_hour
        session_df_new["charging_kw"] = session_df["charging power (kW)"].values

        return session_df_new.set_index("time")

    # --- Apply for each unique session ---
    sessions = []
    for _, group in ev_data.groupby(["started", "ended"]):
        expanded = expand_session(group)
        sessions.append(expanded)

    # --- Combine all sessions ---
    ev_data_new = pd.concat(sessions).sort_index()

    #ev_data_new = ev_data_new.groupby("time", as_index=True)[["power_kw", "energy_kwh"]].sum()
    ev_data_new = ev_data_new.groupby(ev_data_new.index).sum()

    # --- Fill missing hours with 0 ---
    ev_data_new = ev_data_new.asfreq("h", fill_value=0)

    return ev_data_new

def get_ev_data_old():
    ev_data = pd.read_csv('electricityData/zaptec_charging_data.csv')

    ev_data_new = pd.DataFrame()
    ##ev_data_new['time'] = pd.date_range(start=ev_data["started"].iloc[-1].floor('H'),
    #                                   end=ev_data["ended"].iloc[0].floor('H'), freq="H")

    hours = int(ev_data["time"].str.split(" - ").str[0].str.split(":").str[0])
    ev_data_new["time"] = pd.to_datetime(
        ev_data["started"].str.extract(r"(\d{1,2} \w{3} \d{4})")[0] + " " + hour,
        format="%d %b %Y %H",
    )

    current_day = df["start_session"].iloc[0].normalize()
    prev_hour = -1
    for t in hours:
        if hour < prev_hour:  # wrapped around midnight → next day
            current_day += pd.Timedelta(days=1)
        ts = pd.to_datetime(f"{current_day.date()} {t}")
        timestamps.append(ts)
        prev_hour = hour

    # Clean up the power column (remove " kW" and convert to float)
    ev_data_new["charge_kW"] = ev_data["charging power (kW)"].str.replace(" kW", "", regex=False).astype(float)
    # charging sessions might end and start in the same hour so merge duplicate hours by summing
    ev_data_new = ev_data_new.groupby("time", as_index=True)["charge_kW"].sum()

    # Keep only what we need
    ev_data_new = ev_data_new.set_index("time")

    # Resample hourly and fill missing with 0
    ev_data_new = ev_data_new.resample("1H").asfreq().fillna(0)


    ev_data = pd.read_csv('electricityData/zaptec_charging_data.csv')
    ev_data["started"] = pd.to_datetime(ev_data["started"], format="%d %b %Y, %H:%M")
    ev_data["ended"] = pd.to_datetime(ev_data["ended"], format="%d %b %Y, %H:%M")
    ev_data["energy charged"] = ev_data["energy charged"].str.replace("kWh", "", regex=False).astype(float)

    ev_data_new = pd.DataFrame()
    ev_data_new['time'] = pd.date_range(start=ev_data["started"].iloc[-1].floor('5min'), end=ev_data["ended"].iloc[0].floor('5min'), freq="5min")
    ev_data_new['charge_kwh'] = 0.0

    ev_data_new = ev_data_new.set_index("time")

    for _, row in ev_data.iterrows():
        start = row["started"]
        end = row["ended"]
        energy = row["energy charged"]

        five_min_periods = pd.date_range(start.floor("5min"), end.floor("5min"), freq="5min")
        ev_data_new.loc[five_min_periods, 'charge_kwh'] = energy/len(five_min_periods)

    return ev_data_new

def process_hourly_data(tibber_data, pv_data, ev_data):
    # Create hourly_data DataFrame from tibber_data
    hourly_data = pd.DataFrame({
        'hour': tibber_data['From'],
        'price': tibber_data['Price per kWh'],
        'consumption': tibber_data['Consumption']
    })

    # Locate starting index in hourly_data
    pv_start_idx_hourly_data = hourly_data[hourly_data['hour'].dt.date == pv_data['Time'][0].date()].index[0]

    hour_idx = pv_start_idx_hourly_data - 1  # tibber and pv data matches better with 1 hour shift for some reason
    hour_load = 0
    hour_grid_bought = 0
    hour_grid_sold = 0
    hour_pv = 0
    hour_battery_charged = 0
    hour_battery_discharged = 0

    # Iterate over pv_data from the 2nd row onwards (starting at 00:05 seems to better match Tibber hourly consumption)
    for idx, five_min_data in pv_data[1:].iterrows():
        load_val = five_min_data['Load(W)']
        grid_val = five_min_data['Grid(W)']
        pv_val = five_min_data['PV(W)']
        battery_val = five_min_data['Battery(W)']

        if idx != 0 and idx % 12 == 0:
            hourly_data.loc[hour_idx, 'load'] = hour_load
            hourly_data.loc[hour_idx, 'grid_bought'] = hour_grid_bought
            hourly_data.loc[hour_idx, 'grid_sold'] = hour_grid_sold
            hourly_data.loc[hour_idx, 'pv'] = hour_pv
            hourly_data.loc[hour_idx, 'battery_charged'] = hour_battery_charged
            hourly_data.loc[hour_idx, 'battery_discharged'] = hour_battery_discharged
            hourly_data.loc[hour_idx, 'consumed_production'] = max(
                hour_pv + hour_battery_discharged - hour_grid_sold - hour_battery_charged, 0)

            hour_load = 0
            hour_grid_bought = 0
            hour_grid_sold = 0
            hour_pv = 0
            hour_battery_charged = 0
            hour_battery_discharged = 0
            hour_idx += 1
        else:
            if np.isnan(load_val) or np.isnan(hour_load):
                hour_load = np.nan
            else:
                hour_load += load_val * (5 / 60) / 1000

            if np.isnan(grid_val) or np.isnan(hour_grid_bought):
                hour_grid_bought = np.nan
                hour_grid_sold = np.nan
            else:
                if grid_val >= 0:
                    hour_grid_bought += grid_val * (5 / 60) / 1000
                else:
                    hour_grid_sold += -grid_val * (5 / 60) / 1000

            if np.isnan(pv_val) or np.isnan(hour_pv):
                hour_pv = np.nan
            else:
                hour_pv += pv_val * (5 / 60) / 1000

            if np.isnan(battery_val) or np.isnan(hour_battery_charged):
                hour_battery_charged = np.nan
                hour_battery_discharged = np.nan
            else:
                if battery_val >= 0:
                    hour_battery_discharged += battery_val * (5 / 60) / 1000
                else:
                    hour_battery_charged += -battery_val * (5 / 60) / 1000

    hourly_data = hourly_data.set_index('hour')

    # process ev charging data
    hourly_data['ev_charge'] = 0.0
    for _, row in ev_data.iterrows():
        start = row["started"]
        end = row["ended"]
        energy = row["energy charged"]

        # Create hourly time range (inclusive of start hour)
        hours = pd.date_range(start.floor("h"), end.floor("h"), freq="h")

        # Distribute energy evenly across hours
        if len(hours) > 2:
            hours_count = len(hours)-2 + ((60 - start.minute) + end.minute)/60
            energy_per_full_hour = energy / hours_count
            energy_first_hour = energy * ((60 - start.minute) / (hours_count * 60))
            energy_last_hour = energy * (end.minute / (hours_count * 60))

            hourly_data.loc[hours[0], 'ev_charge'] = energy_first_hour
            hourly_data.loc[hours[1:-1], 'ev_charge'] = energy_per_full_hour
            hourly_data.loc[hours[-1], 'ev_charge'] = energy_last_hour
        elif len(hours) == 2:
            hours_count = ((60 - start.minute) + end.minute)/60
            energy_first_hour = energy * ((60 - start.minute) / (hours_count * 60))
            energy_last_hour = energy * (end.minute / (hours_count * 60))

            hourly_data.loc[hours[0], 'ev_charge'] = energy_first_hour
            hourly_data.loc[hours[1], 'ev_charge'] = energy_last_hour
        else:
            hourly_data.loc[hours[0], 'ev_charge'] = energy

    return hourly_data