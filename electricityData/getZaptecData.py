import sys
import csv
import time

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

driver.get('https://portal.zaptec.com/chargeHistory')

# enter username
user_box = safeFindElement(driver, '/html/body/div[1]/div[2]/section/form/div[1]/div/input')
user_box.send_keys('ollefager96@gmail.com')

# enter password
pass_box = safeFindElement(driver, '/html/body/div[1]/div[2]/section/form/div[2]/div/input')
pass_box.send_keys('usasweden')

# login
safeClick(driver, '/html/body/div[1]/div[2]/section/form/button')

# load all content
lastHeight = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Wait for loading

    # Calculate new scroll height and compare
    newHeight = driver.execute_script("return document.body.scrollHeight")
    if newHeight == lastHeight:
        break
    lastHeight = newHeight

charging_session_elements = safeFindElements(driver, '/html/body/div[1]/div[3]/div/div[2]/div/div/table/tbody/*')

charging_sessions = []
for charging_session_element in charging_session_elements:
    session_started = safeFindElement(charging_session_element, './/td[3]').text
    session_ended = safeFindElement(charging_session_element, './/td[4]/div/span').text
    energy_charged = safeFindElement(charging_session_element, './/td[5]').text
    charging_sessions.append([session_started, session_ended, energy_charged])

# Create and write to CSV
with open('C:\\Users\\ollef\\Downloads\\zaptec_charging_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['started', 'ended', 'energy charged'])
    writer.writerows(charging_sessions)