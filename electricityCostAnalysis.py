from helperFunctions import getService
from datetime import date
from datetime import datetime
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import mplcursors

from helperFunctions import read_goteborg_energy_data

def main():
    goteborg_energy_data = read_goteborg_energy_data()
    pv_data = pd.read_csv('electricityData/isolarcloud_hourly_data.csv',
                          na_values=["--"], 
                          parse_dates=[0])
    tibber_data = pd.read_csv('electricityData/tibber_data.csv', 
                              parse_dates=[0,1],
                              date_parser=lambda x: pd.to_datetime(x, utc=True))
    ev_data = pd.read_csv('electricityData/zaptec_charging_data.csv')

    hourly_data = process_hourly_data(tibber_data, pv_data, ev_data)

    #hourly_data['consumption'].plot()
    #hourly_data['grid_bought'].plot()

    grid_price = 0.8
    consumed_production_savings = hourly_data['consumed_production'] * (hourly_data['price'] + grid_price)
    
    #consumed_production_savings.plot()

    #plt.show()

    sheetsService = getService('sheets', 'sheets')
    SPREADSHEET_ID = '1Ri5v7YdwrUEKNGNyvFM6mDyWAjiKzwjwZ1VWCAMl6ds'

    expenses = sheetsService.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                         range='Utgifter!A:F').execute()['values']
    prevMonth = 0
    prevYear = datetime.fromisoformat('2025-01-01').year
    totalCost = 0
    electricityCosts = {prevYear: [0] * 12}

    for iExpense, expense in enumerate(expenses[1:]):
        date = datetime.fromisoformat(expense[0])

        if (date.month != prevMonth and iExpense != 0) or iExpense == len(expenses)-1:
            if date.year != prevYear:
                electricityCosts[prevYear][prevMonth - 1] = totalCost

                electricityCosts[date.year] = [0] * 12

                plt.plot(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec'],
                         electricityCosts[prevYear], label=prevYear)

                prevYear = date.year
            else:
                electricityCosts[date.year][prevMonth-1] = totalCost

            totalCost = 0
        prevMonth = date.month

        receiver = expense[1]
        cost = expense[3]
        if any([receiver == eReceiver for eReceiver in ['Tibber', 'Göteborg Energi']]):
            totalCost += float(cost)

    plt.legend()

    mplcursors.cursor(hover=True)

    plt.show()

def process_hourly_data(tibber_data, pv_data, ev_data):
    # Create hourly_data DataFrame from tibber_data
    hourly_data = pd.DataFrame({
        'hour': tibber_data['From'],
        'price': tibber_data['Price per kWh'],
        'consumption': tibber_data['Consumption']
    })

    # Locate starting index in hourly_data
    pv_start_idx_hourly_data = hourly_data[hourly_data['hour'].dt.date == pv_data['Time'][0].date()].index[0]

    hour_idx = pv_start_idx_hourly_data - 1 # tibber and pv data matches better with 1 hour shift for some reason
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
            hourly_data.loc[hour_idx, 'consumed_production'] = max(hour_pv + hour_battery_discharged - hour_grid_sold - hour_battery_charged, 0)
  
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


    return hourly_data


if __name__ == '__main__':
    main()



