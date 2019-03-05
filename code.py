import datetime
import time
import selenium
import numpy as np
import pandas as pd
from selenium import webdriver
import os
from selenium.webdriver.common.action_chains import ActionChains

chromedriver = webdriver.Chrome()

# Pd option to display more columns
pd.options.mode.chained_assignment = None
pd.set_option('display.expand_frame_repr', False)

# DATA
raw_data_dic = {'slot_id': {0: 1189766, 1: 1237494, 2: 1233539, 3: 1237944, 4: 1216095, 5: 1188167, 6: 1140362, 7: 1201448, 8: 1140008, 9: 1208810},
                'class': {0: 'FrameFitness', 1: 'BikeBeats', 2: 'Gains', 3: 'RippedStripped', 4: 'PumpUpper', 5: 'FalseGrip', 6: 'RippedStripped', 7: 'BarbellClub', 8: 'Kettlebells', 9: 'RippedStripped'},
                'day': {0: 'Monday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Wednesday', 5: 'Wednesday', 6: 'Thursday', 7: 'Thursday', 8: 'Saturday', 9: 'Sunday'},
                'hour': {0: 1815, 1: 1830, 2: 1845, 3: 1800, 4: 1930, 5: 1945, 6: 1845, 7: 1930, 8: 1330, 9: 1100},
                'base_date': {0: 21012019, 1: 25022019, 2: 26022019, 3: 27022019, 4: 23012019, 5: 23012019, 6: 24012019, 7: 24012019, 8: 26012019, 9: 27012019},
                'book_next': {0: 0, 1: 0, 2: 1, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 1}}
gymclass_ids = pd.DataFrame.from_dict(raw_data_dic)
gymclass_ids.drop([2,]) # Drop Gains class that has changed.


# Read class ids. The r before path converts normal string to raw string.
gymclass_ids = pd.DataFrame(gymclass_ids)

# Base_date from integer to date. Get weekday of base date.
gymclass_ids['base_date'] = pd.to_datetime(gymclass_ids['base_date'].astype(str), format='%d%m%Y')
gymclass_ids['base_date_weekday'] = gymclass_ids['base_date'].dt.dayofweek
gymclass_ids['base_date'] = gymclass_ids['base_date'].dt.date


def next_weekday(weekday):
    todaydate = datetime.date.today()
    days_ahead = weekday - todaydate.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return todaydate + datetime.timedelta(days_ahead)

for j in range(gymclass_ids.shape[0]):
    gymclass_ids.loc[j, 'next_date'] = next_weekday(weekday=int(gymclass_ids.loc[j, 'base_date_weekday']))

gymclass_ids['next_date'] = pd.to_datetime(gymclass_ids['next_date'])
gymclass_ids['next_date'] = gymclass_ids['next_date'].dt.date
gymclass_ids['next_date_epoch'] = gymclass_ids.apply(lambda df: (df.next_date - datetime.date(1970, 1, 1)).days,
                                                     axis=1)

next_class = gymclass_ids.iloc[
    pd.to_datetime(gymclass_ids.loc[gymclass_ids['book_next'] == 1, 'next_date']).idxmin()]

# Next class to be booked
# If difference between next class date and today date is 1 or less. Prepare to book second next class
if (next_class['next_date'] - datetime.date.today()).days == 1:
    df_jump = gymclass_ids[gymclass_ids['book_next'] == 1].nlargest(n=2, columns='next_date_epoch', )
    df_jump = df_jump.sort_values(by=['next_date_epoch'])
    next_class = df_jump.iloc[1,]  # Pick second coming date

# Update slot_id variable for next class
next_class['slot_id'] = int(next_class['slot_id']) + (
            (next_class['next_date'] - next_class['base_date']).days % 7) + 1

# Find booking time (7AM of previous day).
# Booking day is clearer than #pd.to_datetime((next_class['next_date'] - datetime.timedelta(days=1))).year
booking_day = next_class['next_date'] - datetime.timedelta(days=1)

# Half million microseconds is half a second
booking_time = datetime.datetime(pd.to_datetime(booking_day).year,
                                 pd.to_datetime(booking_day).month,
                                 pd.to_datetime(booking_day).day,
                                 7, 0, 0, 500000)
# NOT NEEDED IN LAMBDA.
# Difference booking time to today which would be the waiting time.
# sleeping_time = (booking_time - datetime.datetime.now()).total_seconds()

# UPDATED FOR LAMBDA. If sleeping time more than 5 min, return nothing. If less, wait
# Time of sleeping. Stop execution during that time
# time.sleep(sleeping_time)

# Slot id xpath
slot_id_xpath = "//a[@id='slot" + str(next_class['slot_id']) + "']"


# FUNCTIONS

# Handler function for AWS Lambda
def scrape(event, context, slot_id_xpath):
    book_gym_class(slot_id_xpath)


# slot_id = slot_id_xpath
def book_gym_class(slot_id):
    # Surf to web
    chromedriver.get(".....................")

    # Log in process
    EmailElem = chromedriver.find_element_by_xpath("//input[@id='login_Email']")
    EmailElem.send_keys("e-mail")

    PasswordElem = chromedriver.find_element_by_xpath("//input[@id='login_Password']")
    PasswordElem.send_keys("pssssssswrd")

    SubmitElem = chromedriver.find_element_by_xpath("//input[@id='login']")
    SubmitElem.click()

    # Booking
    time.sleep(0.65)
    chromedriver.get("website name")

    # Class slot
    time.sleep(0.3)
    Class_SlotElem = chromedriver.find_element_by_xpath(slot_id)
    Class_SlotElem.click()

    # Confirm process - Finish booking
    time.sleep(0.9)
    Confirm_SlotElem = chromedriver.find_element_by_xpath("//a[@id='btnPayNow']")
    Confirm_SlotElem.click()

    time.sleep(3)
    # Close Chrome Browser
    chromedriver.close()








