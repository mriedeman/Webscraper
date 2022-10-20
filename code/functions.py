# import dependencies
import os
import pandas as pd 
#from splinter import Browser
#from splinter.exceptions import ElementDoesNotExist 
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, TimeoutException
from datetime import date, datetime, timedelta
import holidays
import time

# end_date used to calculate all Mondays for trips
int_stop_date = date(2022, 10, 31)
dom_stop_date = date(2021, 10, 31)

# list of closed holidays
country_holidays = {
    'USA': ("Memorial","Labor","Independence","Thanksgiving","Christmas","New Year's"),
    'CAN': ("New Year's Day","Family Day","Victoria Day","Canada Day","Civic Holiday","Labour Day","Thanksgiving","Remembrance Day","Christmas Day","Boxing Day")
}

# executable_path = {'executable_path':'C:/Users/rbandrowski/AppData/Local/Continuum/anaconda3/chromedriver.exe'}


#THIS APPEARS TO  WORK, MIGHT HAVE TO REVISE LATER
#returns browser with options set and handled
def buildBrowser(executable_path, head=False):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument("--disable-blink-features")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    browser = webdriver.Chrome(executable_path,options = chrome_options)
    
    return browser

#OLD BROWSER FUNCTION USING SPLINTER
# returns browser with options set and handled
# def buildBrowser(executable_path, head=False):
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument('--ignore-certificate-errors')
#     chrome_options.add_argument('--ignore-ssl-errors')
#     chrome_options.add_argument("--disable-blink-features")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
#     chrome_options.add_experimental_option('useAutomationExtension', False)
#     browser = Browser('chrome', options=chrome_options, **executable_path, headless=head)
#     browser.driver.set_window_position(-1915, 20)
#     browser.driver.set_window_size(1900, 1000)
#     browser.driver.set_page_load_timeout(60)
#     return browser


'''Functions for Domestic Scrapes (El Monte, Cruise America)'''
# function to filter all holidays down to closed holidays
def domHolidayClosures(country_holidays, US):
    year = date.today().year
    years = [year, year + 1]
    if US:
        holiday_days = country_holidays['USA']
        country = list(holidays.US(years=years).items())
    else:
        holiday_days = country_holidays['CAN']
        country = list(holidays.CA(years=years).items()) + [(date(x, 11, 11), "Remembrance Day") for x in years]

    for item in holiday_days:
        for x in country:
        # for x in intHolidays(date.today().year, date.today().year + 1, date.today().year + 2):
            if item in x[1]:
                yield x[0]

# function to generate list of all mondays after today, until end of year
def allFridays(dom_stop_date):
    d = date.today()
    while d.weekday() != 4:
        d += timedelta(1)
    while d <= dom_stop_date:
        yield d
        d += timedelta(days=7)


'''Functions for International Tour Operator Scrapes'''
# function to filter all US or CA holidays down to closed holidays
def intHolidayClosures(country_holidays, US):
    year = date.today().year
    years = [year, year + 1, year + 2]
    if US:
        holiday_days = country_holidays['USA']
        country = list(holidays.US(years=years).items())
    else:
        holiday_days = country_holidays['CAN']
        country = list(holidays.CA(years=years).items()) + [(date(x, 11, 11), "Remembrance Day") for x in years]
    
    for item in holiday_days:
        for x in country:
        # for x in intHolidays(date.today().year, date.today().year + 1, date.today().year + 2):
            if item in x[1]:
                yield x[0]

# function to generate list of mondays
def allMondays(int_stop_date):
    d = date.today()
    # d = date(2022, 1, 1)
    d += timedelta(7 - d.weekday())
    while d <= int_stop_date:
        yield d
        d += timedelta(days = 7)


'''Functions to generate filenames for output data'''
# function to create output filename
def createFilename(site, log=False):
    d = date.today()
    while d.weekday() != 3:
        d += timedelta(1)
    d = d.strftime('%m-%d-%Y')
    try: 
        os.makedirs(f'../Output Data/{d}')
    except FileExistsError:
        pass
    try: 
        os.mkdir(f'../Output Data/{d}/International')
    except FileExistsError:
        pass
    try:
        os.mkdir(f'../Output Data/{d}/Logs')
    except FileExistsError:
        pass
    if log:
        filename = f'../Output Data/{d}/Logs/{site} Data Log.txt'
    else:
        filename = f'../Output Data/{d}/International/{site} Data {d}.csv'
    return filename

# function to create output filename for wednesday trips
def createWedFilename(site):
    d = date.today()
    while d.weekday() != 3:
        d += timedelta(1)
    d = d.strftime('%m-%d-%Y')
    try: 
        os.mkdir(f'../Output Data/{d}')
    except FileExistsError:
        pass
    try: 
        os.mkdir(f'../Output Data/{d}/International')
    except FileExistsError:
        pass
    filename = f'../Output Data/{d}/International/{site} Wed. Data {d}.csv'
    return filename

# function to create output filename for domestic scrapes
def createDomFilename(site, log=False):
    d = date.today()
    while d.weekday() != 3:
        d += timedelta(1)
    d = d.strftime('%m-%d-%Y')
    try: 
        os.mkdir(f'../Output Data/{d}')
    except FileExistsError:
        pass
    try: 
        os.mkdir(f'../Output Data/{d}/Domestic')
    except FileExistsError:
        pass
    try:
        os.mkdir(f'../Output Data/{d}/Logs')
    except FileExistsError:
        pass
    if log:
        filename = f'../Output Data/{d}/Logs/{site} Data Log.txt'
    else:
        filename = f'../Output Data/{d}/Domestic/{site} Data {d}.csv'
    return filename


'''Template for function to create trips, individual ones used in each scrape based on needs for website'''
# function to generate list of trips for US & CA

def create_trips(int_stop_date, US):
    for pu_d in allMondays(int_stop_date):

        pu_d += timedelta(14)
        # drop off date is 17 days after today
        do_d = pu_d + timedelta(17)
        # Wed to Wed trips
        pu_w = pu_d + timedelta(2)
        do_w = pu_w + timedelta(7)
        # for all mondays after today
        if pu_d > date.today() + timedelta(10):
            # if monday is a holiday, change pickup to Tuesday
            if pu_d in intHolidayClosures(country_holidays, US):
                pu_d += timedelta(1)
            if pu_w in intHolidayClosures(country_holidays, US):
                pu_w -= timedelta(1)
            # if Thursday is a holiday, change drop off to Wednesday
            if do_d in intHolidayClosures(country_holidays, US):
                do_d -= timedelta(1)
            if do_w in intHolidayClosures(country_holidays, US):
                do_w += timedelta(1)

            yield {'start_date':pu_d.strftime('%Y-%m-%d'),'start_day': pu_d.strftime('%d').lstrip('0'),'start_month': pu_d.strftime('%b'),'start_year': pu_d.strftime('%Y'),
                   'start_wed_date':pu_w.strftime('%Y-%m-%d'),'start_wed_day': pu_w.strftime('%d').lstrip('0'),'start_wed_month': pu_w.strftime('%b'),'start_wed_year': pu_w.strftime('%Y'),
                   'end_date':do_d.strftime('%Y-%m-%d'),'end_day':do_d.strftime('%d').lstrip('0'),'end_month':do_d.strftime('%b'),'end_year':do_d.strftime('%Y'),
                   'end_wed_date':do_w.strftime('%Y-%m-%d'),'end_wed_day':do_w.strftime('%d').lstrip('0'),'end_wed_month':do_w.strftime('%b'),'end_wed_year':do_w.strftime('%Y')}