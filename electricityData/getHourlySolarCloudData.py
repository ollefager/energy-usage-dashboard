import sys
import time
import pandas as pd
import glob
import os

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

sys.path.append('../..')
from helperFunctions import safeClick, safeFindElement, safeFindElements, getGitRoot, getService

# Using Chrome to access web
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_experimental_option('prefs', {"safebrowsing_for_trusted_sources_enabled": False,
                                                "safebrowsing.enabled": False})
chromeOptions.add_argument('--no-sandbox')
chromeOptions.add_argument('--remote-debugging-port=9222')
chromeOptions.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=chromeOptions)
driver.maximize_window()

driver.get('https://web3.isolarcloud.eu/#/plantDetail/overView')

safeClick(driver, '//*[@id="app"]/div[1]/div[2]/div[2]/button[3]')

# enter username
user_box = safeFindElement(driver, '/html/body/div[1]/div[1]/div[3]/div[2]/form/div[1]/div/div/div/input')
user_box.send_keys('ollefager96@gmail.com')

# enter password
pass_box = safeFindElement(driver, '/html/body/div[1]/div[1]/div[3]/div[2]/form/div[2]/div/div/div/input')
pass_box.send_keys('USA-sweden96')

# login
safeClick(driver, '//*[@id="app"]/div[1]/div[3]/div[2]/form/div[4]/div/button')
# go to overview
safeClick(driver, '//*[@id="app"]/div[1]/div[2]/div[2]/div[1]/div/div/div/div[1]/div[3]/div[2]/div[1]/div[3]/div/div[1]/div/table/tbody/tr/td[1]/div/div/a')

fulldata_file = 'C:\\Users\\ollef\\Downloads\\isolarcloud_hourly_data.csv'
backButtonIsClickable = True
while backButtonIsClickable:
    # export day data
    safeClick(driver, '/html/body/div[1]/div[1]/div[2]/div[2]/div[1]/div/div/div/div[2]/div[2]/div[1]/div/div[1]/div[3]/div[2]/div[2]/div[1]/div[2]/span[2]/div/div/div/p')
    actions = ActionChains(driver)
    actions.move_by_offset(1, 1)
    actions.perform()
    safeClick(driver, '/html/body/div[2]/div[16]/div/div[1]/div/ul/li[2]')
    last_downloaded_file = max(glob.glob('C:\\Users\\ollef\\Downloads\\*'), key=os.path.getmtime)

    # add day data to full data
    full_df = pd.read_csv(fulldata_file)
    day_df = pd.read_csv(last_downloaded_file).iloc[::-1]
    combinedDf = pd.concat([full_df, day_df], ignore_index=True)
    combinedDf.to_csv(fulldata_file, index=False)
    if last_downloaded_file != fulldata_file:
        os.remove(last_downloaded_file)
    try:
        safeClick(driver, '//*[@id="plant-detail-overview-mount-loading-node"]/div[1]/div/div[1]/div[3]/div[1]/div[2]/span[1]')
    except:
        backButtonIsClickable = False