from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException, JavascriptException, NoSuchElementException
import time
from datetime import date, datetime, timedelta 
import numpy as np
import pandas as pd
import os
from functions import allMondays, intHolidayClosures, create_trips, country_holidays



#create browser
s=Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=s)
url = 'https://www.campertravelusa.com/'
browser.get(url)

#load webpage
delay = 3 # seconds
try:
    myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH,"//input[contains(@id, 'pickupLocation')]")))
    print ("Page is ready!")
except TimeoutException:
    print ("Loading took too much time!")



cities = [{'city':'San Francisco','state':'CA', 'abbr':'SFO', 'country':'USA'},
          {'city':'Las Vegas','state':'NV', 'abbr':'LAS', 'country':'USA'},
          {'city':'Los Angeles','state':'CA', 'abbr':'LAX', 'country':'USA'},
          {'city':'Seattle','state':'WA', 'abbr':'SEA', 'country':'USA'},
          {'city':'Salt Lake City','state':'UT', 'abbr':'SLC', 'country':'USA'},
          {'city':'Denver','state':'CO', 'abbr':'DEN', 'country':'USA'},
          {'city':'Chicago','state':'IL', 'abbr':'CHI', 'country':'USA'},
          {'city':'Dallas','state':'TX', 'abbr':'DFW', 'country':'USA'},
          {'city':'Orlando','state':'FL', 'abbr':'MCO', 'country':'USA'}]

#picks the driver's license first because you only need to pick it once
browser.find_element(By.CSS_SELECTOR, 'input.form-control.X-CountryOfResidence.AutoCompleteSelectInput').click()
time.sleep(int(np.random.rand(1)*8))

try:
    myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.XPATH,"//div[@class = 'autocomplete-suggestion'][@data-val = 'International']")))
    print ("autcomplete-suggestion element is ready")
    #browser.find_element(By.XPATH, "//div[@class = 'autocomplete-suggestion'][@data-val = 'International']").click()
except TimeoutException:
    print("Loading took too much time!")

browser.find_element(By.XPATH, "//div[@class = 'autocomplete-suggestion'][@data-val = 'International']").click()

for city_index, city in enumerate(cities):
    #browser.find_element(By.XPATH,"//input[contains(@id, 'pickupLocation')]").clear()
    browser.find_element(By.XPATH,"//input[contains(@id, 'pickupLocation')]").click()
    time.sleep(int(np.random.rand(1)*8))

    browser.find_element(By.XPATH,"//input[contains(@id, 'pickupLocation')]").send_keys(city['city'])
    time.sleep(int(np.random.rand(1)*8))
    browser.find_element(By.XPATH,"//*[@id='c1-5-2-widget-pickupLocation']").send_keys(Keys.RETURN)
    time.sleep(int(np.random.rand(1)*8))

    print(f"Collecting Results for {city['city']}")


    int_stop_date = date(2022, 9, 30) #turn this into a parameter

    US = True if city['country'] == 'USA' else False
    city_results = []


    for trip_index, trip in enumerate(create_trips(int_stop_date, US)):

    

        print(F"ITERATION {trip_index}")
        time.sleep(1.5)

        #open the calendar
        browser.find_element(By.XPATH, "//*[@id='c1-5-2-widget-pickupDate']").click()
        time.sleep(int(np.random.rand(1)*7))
        cal_month = browser.find_element(By.XPATH,"//div[@class = 'dr-cal-start']/div/div/div").find_element(By.CSS_SELECTOR,'button.dp-cal-month').text[0:3]

        time.sleep(3)

        

        while cal_month != trip['start_month']:
            browser.find_element(By.XPATH, "//div[@class = 'dr-cal-end']/div/div/div/header/button[@class = 'dp-next']").click()
            #updates cal_month variable to whatever date you are currently on
            cal_month = browser.find_element(By.XPATH,"//div[@class = 'dr-cal-start']/div/div/div").find_element(By.CSS_SELECTOR,'button.dp-cal-month').text[0:3]
            time.sleep(int(np.random.rand(1)*3))
            print(cal_month)

        pu_d = browser.find_element(By.XPATH, f"//div[@class = 'dr-cal-start']/div/div/div/div/button[not(contains(@class, 'edge-day'))][text() = {trip['start_day']}]")
        pu_d.click()

        time.sleep(2)


        #picks the end day, if the start day is smaller than the end day the first page is picked, otherwise the next month's page is picked
        if int(trip['start_day']) < int(trip['end_day']):
            do_d = browser.find_element(By.XPATH, f"//div[@class = 'dr-cal-start']/div/div/div/div/button[not(contains(@class, 'edge-day'))][text() = {trip['end_day']}]")
        else:
            do_d = browser.find_element(By.XPATH, f"//div[@class = 'dr-cal-end']/div/div/div/div/button[not(contains(@class, 'edge-day'))][text() = {trip['end_day']}]")
        do_d.click()
        
        
        #click the search button
        time.sleep(int(np.random.rand(1)*5))
        browser.find_element(By.CSS_SELECTOR, 'button.btn.btn-success.btn-lg.btn-block.X-SearchButton').click()

        print("SEARCHING...")

        time.sleep(3)

        #remove pop-up and switch windows
        browser.execute_script("document.querySelector('#hbl-live-chat-wrapper').style.display = 'none';")
        browser.switch_to.window(browser.window_handles[1])
        
        #load page
        try:
            myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.campervan-result')))
            print ("Page is ready!")
        except TimeoutException:
            print ("Loading took too much time!")

        browser.switch_to.window(browser.window_handles[1])
        
        
        
        pixels = 0
        webelements = []
        trip_data = []
        scroll_height = browser.execute_script("return document.body.scrollHeight")
        
        print(f"The scroll height is {scroll_height} for webpage results regarding {trip['start_date']} leaving {city['city']}.")

        while pixels < scroll_height:
            results = browser.find_elements(By.CLASS_NAME, 'campervan-result')
            time.sleep(1.5)
            browser.execute_script(f"window.scrollTo(0, {pixels});")

            for result in results:
                if result not in webelements:
                    webelements.append(result)

                    total_price = result.find_element(By.CLASS_NAME, 'X-VPrice-ConvertedFrom-Amount-Dollars').text
                    daily_price = result.find_element(By.CSS_SELECTOR, 'div.quote-daily-price span.X-VPrice-ConvertedFrom-Amount-Dollars').text
                    vehicle_class = result.find_element(By.CSS_SELECTOR, 'span.vehicle-name-text').text
                    company_name = result.find_element(By.CSS_SELECTOR,'div.result-supplier img').get_attribute('alt')
                    trip_data.append({
                        'city':city['city'],
                        'start_date':trip['start_date'],
                        'end_date':trip['end_date'],
                        'total_price':total_price,
                        'daily_price': daily_price,
                        'vehicle_class':vehicle_class,
                        'company_name':company_name
                        })

            pixels += 500

        
        city_results = city_results + trip_data
        browser.close()

        browser.switch_to.window(browser.window_handles[0])


    city_results_df = pd.DataFrame(city_results)


    try: 
        os.makedirs(f"../Output Data/Camper Travel/{city['city']}")
    except FileExistsError:
        pass

    city_results_df.to_csv(f"../Output Data/Camper Travel/{city['city']}/{city['city']} {date.today()}.csv", index=False)

    print(f"Saved Results of {city['city']} to a csv file.")


print("Script Finished Running")