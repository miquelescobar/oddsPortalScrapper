# Module that contains auxiliar functions and tools


####################################################################################################
############################################## IMPORT ##############################################
####################################################################################################

# Import required modules
# Selenium webdriver and ActionChains
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options

import json
import numpy as np
# Import calendar
from calendar import monthrange



#%%#################################################################################################
############################################ CONSTANTS #############################################
####################################################################################################

# DEFINING CONSTANTS
# Driver paths
CHROME_PATH      = '/usr/local/bin/chromedriver'
PHANTOMJS_PATH   = ''
FIREFOX_PATH     = '/usr/local/bin/geckodriver'
# Define webdriver options
WEBDRIVER = 'chrome'
HEADLESS = True



#%%#################################################################################################
######################################## TOOLS / FUNCTIONS #########################################
####################################################################################################

def login(driver, data_payload):
    """ Function to login into oddsPortal user """
    
    # Go to login url
    driver.get(data_payload['login_url'])
    
    # Select user and password text boxes
    username = driver.find_element_by_name("login-username")
    password = driver.find_element_by_name("login-password")
    username.clear()
    password.clear()
    
    # Write user and password to text boxes
    username.send_keys(data_payload['user'])
    password.send_keys(data_payload['password'])
    
    # Click login button
    submit = driver.find_element_by_css_selector("#main button[name=login-submit]")
    submit.click()
    


def get_webdriver(webdriver_name=WEBDRIVER, headless=HEADLESS):
    """ Returns the webdriver object """
    
    # Case CHROME
    if webdriver_name.lower() == 'chrome':
        # Define options and eliminate charging images
        options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2, 'disk-cache-size': 4096 }
        options.add_experimental_option('prefs', prefs)
        # Make it headless if required
        if headless: options.add_argument('headless')
        # Define and return webdriver
        driver = webdriver.Chrome(CHROME_PATH, options=options)
        return driver


    # Case FIREFOX
    if webdriver_name.lower() == 'firefox':
        options = Options()
        if headless: options.headless = True
        driver = webdriver.Chrome(options=options, executable_path=FIREFOX_PATH)
        return driver
    

#%%#################################################################################################
######################################## TOOLS / FUNCTIONS #########################################
####################################################################################################

def read_json(filename):
    """ Function to read data saved in a .json file """
    
    with open(filename, 'r') as input_file:
        data = json.load(input_file)
        print("Read data from %s of type %s" % (filename, type(data)))
        return data


def write_json(data, filename):
    """ Function to write data into a .json file """
    
    with open(filename, 'w') as output_file:
        json.dump(data, output_file)
        print("Written data to %s of type %s" % (filename, type(data)))


def generate_seasons(start, final):
    """ Function to generate an array of seasons from start to final """
    
    func = np.vectorize( lambda s: str(s) + '-' + str(s+1) )
    return func( np.arange(start, final) )


def max_in_interval(array, min_val, max_val):
    """ Function to get the maximum of a lost given an interval """
    
    return max([val for val in array if (val >= min_val and val <= max_val)])


def season_urls_filepath_eu(country, division, str_season, country_to_code):
    """ Function to obtain the filepath to season urls (Europe) """
    
    return ('../Storage/Games_URLS/Europe/' + country_to_code[country] + division + '/'
            + country_to_code[country] + division + '_URLS_' + str_season +'.csv')
    
    
def same_gameweek(game_date, last_date):
    """ Function that returns true if two dates belong to the same week 
        or false otherwise """
    day, month, year = game_date.day, game_date.month,  game_date.year
    last_day, last_month = last_date.day, last_date.month
    
    return ( (abs(last_day - day) <= 1 and month == last_month) or
             (day == max(monthrange(year, month)) and last_day == 1) )
    
    
def clean_game_dict(D):
    """ Eliminates unnecessary data and modifies incompatible formats
        in the dictionary of the class """
    
    # Timestamp to string
    D['date'] = str(D['date'])
    D['time'] = str(D['time'])
    
    for bet_type in D['bet_types_data']:
        # Check not-NULL dictionary
        if D['bet_types_data'][bet_type]:
            # Delete unnecessary objects
            for attribute in ('game', 'bet_type', 'columns'):
                del D['bet_types_data'][bet_type][attribute]
            # Convert DataFrame to JSON
            if D['bet_types'][bet_type]['type'] == 1:
                D['bet_types_data'][bet_type]['odds_table'] =  D['bet_types_data'][bet_type]['odds_table'].to_json()
                D['bet_types_data'][bet_type]['hist_odds_table'] =  D['bet_types_data'][bet_type]['hist_odds_table'].to_json()
            else:
                d = D['bet_types_data'][bet_type]['odds_tables']
                D['bet_types_data'][bet_type]['odds_tables'] = {k:v.to_json() for k,v in d.items()}
                d2 = D['bet_types_data'][bet_type]['hist_odds_tables']
                D['bet_types_data'][bet_type]['hist_odds_tables'] = {k:v.to_json() for k,v in d2.items()}
                del D['bet_types_data'][bet_type]['td']
                del D['bet_types_data'][bet_type]['url_aux']
                
    # Delete unnecessary/redundant data
    del D['bookmakers']
    del D['bet_types']
    del D['driver']
    
    # Return clean dicitonary
    return D
    
    
    