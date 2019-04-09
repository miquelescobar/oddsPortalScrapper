# Module that contains classes and functions related with oddsPortal website


####################################################################################################
############################################## IMPORT ##############################################
####################################################################################################

# Import required modules
# Selenium webdriver and ActionChains
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
# Urllib and bs4 to scrap html code
from bs4 import BeautifulSoup
from urllib.parse import urljoin
# Pandas for dataFrames
import pandas as pd
# Numpy for arrays and its mathematical functions
import numpy as np
# Using re for string parsing and searches
import re
# For timing processes
import time
from datetime import datetime as timer

from tools import * #read_json, write_json, read_json, max_in_interval, get_webdriver, login, clean_game_dict

from betTypes.HDA import HDA


#%%#################################################################################################
########################################## INITIALIZATION ##########################################
####################################################################################################

# LOAD DICTIONARY DATA FILE
# Country <-> country code conversion dictionaries
code_to_country  = read_json('../config/code_to_country.json')
country_to_code  = read_json('../config/country_to_code.json')
# Basic data to acces OddPortal website
odds_portal_data = read_json('../config/odds_portal_data.json')
odds_portal_data['date_pattern'] = re.compile(odds_portal_data['date_pattern'], re.UNICODE)
# Country and division to league name conversor
leagues_names    = read_json('../config/leagues_names.json')

# DEFINING CONSTANTS
# Driver paths
CHROME_PATH      = '/usr/local/bin/chromedriver'
PHANTOMJS_PATH   = ''
FIREFOX_PATH     = '/usr/local/bin/geckodriver'
# Define webdriver options
WEBDRIVER = 'chrome'
HEADLESS = True

    
#%%#################################################################################################
############################################# CLASSES ##############################################
####################################################################################################
   

class League:
    
    
    def __init__(self, country, division):
        """ League Class """
        
        # Define country, division, name, driver, url variables
        self.country  = country
        self.division = division
        self.names    = leagues_names[country][division]
        self.url      = ( odds_portal_data['soccer_parent_url']
                          + country.lower() + '/' )
        self.driver   = get_webdriver()
        login(self.driver, odds_portal_data)
        
        
    def create_season_games_url(self, str_season, save=False):
        """ Generates url of a specific season results """
        
        season_name = self.names[max_in_interval(self.names, min(self.names), str_season)]
        return ( self.url + season_name + '-' + str_season + '/results/' )
    
    
    def get_season_games_urls(self, str_season, save=False):
        """ Get the games urls for an entire season.
            Define save as True to save the data into a .json file """

        url = self.create_season_games_url(str_season)
        self.driver.get(url)
        games_urls = []
        
        pages_html = self.driver.find_element_by_id('pagination').get_attribute("innerHTML")
        pages_soup = BeautifulSoup(pages_html, 'html.parser')
        pages      = [url] + [urljoin(url, page['href']) 
                              for page in pages_soup.find_all('a')[2:-2]]
        
        for page in pages:
            self.driver.get(page)
            self.driver.refresh()
            #time.sleep(5)
            table_html = self.driver.find_element_by_id('tournamentTable').get_attribute("innerHTML")
            table_soup = BeautifulSoup(table_html, 'html.parser')
            page_urls  = [urljoin(url, item.find('a').get('href')) for item in 
                          table_soup.find_all('td', {'class':"name table-participant"})]
            games_urls.extend(page_urls)

        
        #!!!#
        save_path = ('../Storage/Games_URLS/Europe/' + country_to_code[self.country] + self.division + '/'
                     + country_to_code[self.country] + self.division + '_URLS_' + str_season +'.csv')
        if save: write_json(games_urls, save_path)
        #!!!#
        
        if len(games_urls) == len(set(games_urls)): 
            print(self.country + " " + self.division + " has been correctly read.")
            return games_urls
        
        raise ConnectionError('Connection was too bad for the data collection. Please try again.')
        




class Game:
    
    
    ######################################### CONSTRUCTOR ##########################################

    def __init__(self, 
                 url, webdriver_name='Chrome', headless=True, driver=None,
                 bookmakers=odds_portal_data['bookmakers'], save=False ):
        """ Game Class """

        start = timer.now()
        # Define driver and url variables
        self.url         = url
        self.webdriver   = webdriver_name
        self.headless    = headless
        
        # Prepare driver
        if (driver):
            # Precodnitions: driver legged into oddsPortal account
            self.driver  = driver
        else: 
            self.driver  = get_webdriver(webdriver_name=webdriver_name, headless=headless)
            # Login and go to game url
            login(self.driver, odds_portal_data)
            self.driver.get(url)
        
        # Define game data variables
        self.bookmakers  = bookmakers
        self.division    = '1'
        self.country     = url.split('/')[4].title()
        self.continent   = 'Europe'
        self.league      = self.get_league()
        self.finished    = self.played()
        self.league      = self.get_league()
        self.home_team   = self.get_home_team()
        self.away_team   = self.get_away_team()
        self.date        = self.get_date()
        self.score       = self.get_score()
        self.result      = self.get_result()
        self.description = (self.home_team + ' - ' + self.away_team + ', ' + str(self.date))
        self.filename    = '_'.join((str(self.date.year), str(self.date.month), str(self.date.day), self.home_team, self.away_team)) + '.json'
    
        #print('Starting scrap at game', self.description)    
        # Declare bet types and scrap their data
        self.bet_types = odds_portal_data['bet_types_props']
        self.bet_types_data = {}
        self.scrap_data(self.bet_types)
        self.time        = timer.now()-start
        #print('Finsihed scrap at game', self.description, 'within', self.time)
        self.driver.close()
        self.driver.quit()
        self.driver = None
        #print(self.description, 'saved at file', self.filename, 'and driver.quit() executed')
        
    
    ###################################### REGULAR FUNCTIONS #######################################
    def save(self):
        """ Saves the class as a dict to a json file """
        
        if (self.save):
            outputFile = '../Storage/Games_Data/' + self.continent + '/' + self.league + '/' + self.filename
            write_json(clean_game_dict(self.__dict__), outputFile)
        

    def restart_driver(self):
        """ Restarts the driver just in case an error occurs """
        
        self.driver = get_webdriver(webdriver=self.webdriver, headless=self.headless)
        # Login and go to game url
        login(self.driver, odds_portal_data)
        self.driver.get(self.url)
        
        
    def get_league(self):
        """ Get the league of the game """
        
        return country_to_code[self.country] + self.division
    
    
    def get_home_team(self):
        """ Get home team of the game """
        
        element = self.driver.find_element_by_xpath('//*[@id="col-content"]/h1').get_attribute("innerHTML")
        return element.split(' - ')[0].replace(' ','')
    
    
    def get_away_team(self):
        """ Get away team of the game """
        
        element = self.driver.find_element_by_xpath('//*[@id="col-content"]/h1').get_attribute("innerHTML")
        return element.split(' - ')[1].replace(' ','')
        
    
    def get_date(self):
        """ Get date of the game """
        
        element = self.driver.find_element_by_xpath('//*[@id="col-content"]/p[1]').get_attribute('innerHTML')
        # Check if yesterday, today or tomorrow is in date string 
        if   'Yesterday' in element: element = element.replace('Yesterday, ', '')
        elif 'Today'     in element: element = element.replace('Today, '    , '')
        elif 'Tomorrow'  in element: element = element.replace('Tomorrow, ' , '')
        # Return date in pandas datetime format
        return pd.to_datetime(element)
    
    
    def played(self):
        """ Returns true if game has been played, false otherwise """
        
        element = self.driver.find_element_by_xpath('//*[@id="col-content"]').get_attribute("innerHTML")
        if 'Final result' in str(element): return True
        return False
    
        
    def get_score(self):
        """ Get score data of the game """

        # If the game has not been played, return no score
        if (not self.finished): return None
        # Otherwise, return score
        element = self.driver.find_element_by_xpath('//*[@id="event-status"]').get_attribute('innerHTML')
        soup    = BeautifulSoup(element, 'html.parser')
        # Parse the string to separate data elements
        score   = soup.text.replace('Final result ', '').replace(',', ')')
        score   = score[:score.index(')')+1].replace(')', '').split(' (')
        # Get indexes to parse values in dictionary
        i, i2   = score[0].index(':'), score[1].index(':')
        # Return a dictionary
        return {'FT_Home_Goals':score[0][:i], 'FT_Away_Goals':score[0][i+1:],
                'HT_Home_Goals':score[1][:i2], 'HT_Away_Goals':score[1][i2+1:]}
        
        
    def get_result(self):
        """ Get result data of the game """
        
        # If the game has not been played, return no result
        if (not self.finished): return None
        # Otherwise, return result
        score = self.get_score()
        # Find out fulltime result
        if   score['FT_Home_Goals'] > score['FT_Away_Goals']: FTR = 'H'
        elif score['FT_Home_Goals'] < score['FT_Away_Goals']: FTR = 'A'
        else:                                                 FTR = 'D' 
        # Find out halftime result
        if   score['HT_Home_Goals'] > score['HT_Away_Goals']: HTR = 'H'
        elif score['HT_Home_Goals'] < score['HT_Away_Goals']: HTR = 'A'
        else:                                                 HTR = 'D' 
        # Return dictionary
        return {'FTR':FTR, 'HTR':HTR}
    
    
    def find_bet_type(self, bet_type):
        """ For bet_types ['Winner','1X2','Home/Away','AH','O/U','DNB','EH','TQ','CS','HT/FT','O/E','BTS','More bets', etc.]
            returns True if the bet_type data is available in the Game (oddsPortal) """
        
        # Get bet_types headers html code 
        bet_types_html = self.driver.find_element_by_xpath('//*[@id="bettype-tabs"]').get_attribute("innerHTML")
        soup = BeautifulSoup(bet_types_html, 'html.parser')
        
        # Iterate through headers to find the bet_type displayed
        for header in soup.find_all('li'):
            if bet_type in str(header) and header.get('style') != 'display: none;':
                return True
            
        # Iterate through others headers html code
        for header in soup.find_all('li', {"class":"r more "}):
            if bet_type in header.text:
                return True
            
        # If bet_type not displayed, return False
        return False
    
    
    ##################################### BET TYPES FUNCTIONS #######################################
        
    def scrap_data(self, bet_types):
        """ Scraps all bet types data available from the game """
        
        #start = timer.now()
        # Iterates through all bet_types specified
        for bet_type in bet_types:
            # If bet_type is available
            if self.find_bet_type(bet_type):
                # Go to bet_type url
                self.driver.get(self.url + '#' + self.bet_types[bet_type]['url_aux'] + ';2')
                self.driver.refresh()
                # Generate corresponding class to bet_type and save data
                if self.bet_types[bet_type]['type'] == 1:  self.bet_types_data[bet_type] = self.TYPE_1(self, bet_type).__dict__
                else:                                      self.bet_types_data[bet_type] = self.TYPE_2(self, bet_type).__dict__
            # If bet_type not available
            else: 
                self.bet_types_data[bet_type] = None
                #print('No data available for', bet_type, 'in game', self.description)
        #print('Data scrapping duration for game', self.description ,':', timer.now()-start)
                
    
    ###################################### BET TYPES CLASSES #######################################
    
    class TYPE_1:
        
        # CONSTRUCTOR
        
        def __init__(self, game, bet_type):
            """ Constructor function """
            
            # Define the game class and bet_type
            self.game            = game
            self.bet_type        = bet_type
            self.columns         = game.bet_types[bet_type]['columns']
            
            # Define the odds DataFrames
            self.odds_table      = self.get_odds_table()
            self.hist_odds_table = self.get_hist_odds_table()
        
        
        # CONSTRUCTOR FUNCTIONS
        
        def get_odds_table(self):
            """ Function to get current odds table """
            
            # Find the table in the page (html format) and convert it to a pandas DataFrame
            table_html = self.game.driver.find_element_by_xpath('//*[@id="odds-data-table"]').get_attribute("innerHTML")
            # Convert html table to DataFrame
            odds_table = pd.read_html(table_html)[0] 
            # Format the DataFrame to the desired format
            odds_table.index = odds_table['Bookmakers']
            odds_table = odds_table[odds_table.index.isin(self.game.bookmakers)][self.columns]
            #odds_table = odds_table[:-2]#.dropna(axis=0)
            odds_table = odds_table.apply(pd.to_numeric, errors='ignore')
            # Returns the DataFrame
            return odds_table
        
        
        def get_hist_odds_table(self):
            """ Function to get historical odds table """
            
            # Get shape and as a base the odds table
            R, C = self.odds_table.shape
            hist_odds_table = self.odds_table.copy()
            # Iterate through all odds to scrap their respective historical odds
            for i in range(R):
                for j in range(C):
                    # Search for xpath and perform an action to obtain data in the pop-up bubble 
                    XPATH       = ('//*[@id="odds-data-table"]/div[1]/table/tbody/tr[%d]/td[%d]/div'
                                   % (i+1,j+2), )[0]
                    # It is either raw text (div) or a link (a)
                    try:    element = self.game.driver.find_element_by_xpath(XPATH)
                    except: 
                        try:    element = self.game.driver.find_element_by_xpath(XPATH[:-3]+'a')
                        except: break
                    
                    # If historical data bubble not available, save only entry
                    try:
                        ActionChains(self.game.driver).move_to_element(element).perform()
                        bubble      = self.game.driver.find_element_by_xpath("//*[@id='tooltiptext']")
                        bubble_data = bubble.get_attribute("innerHTML")
                        data = {}
                        # Convert bubble html code to dictionary with dates as keys and odds as values
                        for date in re.findall(odds_portal_data['date_pattern'], bubble_data):
                            i1 = bubble_data.find(date)
                            i2 = bubble_data[i1:].find('</strong>') + i1
                            key, value = bubble_data[i1:i2].split('  <strong>')
                            data[key]  = value
                        # Assign to each DataFrame cell its respective dictionary
                        hist_odds_table.iloc[i,j] = str(data)
                        
                    except:
                        hist_odds_table.iloc[i,j] = str({self.game.date:self.odds_table.iloc[i,j]})
                        
            # Returns the DataFrame
            return hist_odds_table
        
        
        
    class TYPE_2:
        
        # CONSTRUCTOR
        
        def __init__(self, game, bet_type):
    
            # Define the game class
            self.game             = game
            self.bet_type         = bet_type
            self.columns          = game.bet_types[bet_type]['columns']
            self.url_aux          = game.bet_types[bet_type]['url_aux']
            self.td               = game.bet_types[bet_type]['td']
            
            # Define game's over/under url
            self.url    = self.get_url()
            
            # Define available values and corresponding <div> indexes
            #self.values           = self.get_values()
            #self.available_values = self.values[0]
            #self.values_div_index = self.values[1]
            #self.bookmakers_cnt   = self.values[2]
            
            # Define dictionaries to save odds tables and avoid repeting scrapping
            self.odds_tables      = {}
            self.hist_odds_tables = {}
            
            # Scrap all tables option
            self.get_all_tables()
            
       
        # CONSTRUCTOR FUNCTIONS
        
        def get_url(self): 
            """ Returns the game's url for european handicap bets """
            
            return self.game.url + '#' + self.url_aux + ';2;'
        
        
        def get_all_tables(self):
            """ Gets and saves all tables (current and historical) to the class """
            
            # Counts how many values there are
            html = self.game.driver.find_element_by_xpath('//*[@id="odds-data-table"]').get_attribute('innerHTML')
            divs = len(BeautifulSoup(html, 'html.parser').find_all('div', {'class':'table-container'})) + 2
            div = 1
            # Iterates through all values
            while div < divs:
                # Checks if the table is available
                try: 
                    # Opens the table
                    element = self.game.driver.find_element_by_xpath('//*[@id="odds-data-table"]/div[%d]/div/strong/a' % div)
                    element.click()
                except: 
                    div += 1
                    continue
                # Gets the value name
                html = element.get_attribute('innerHTML')
                soup = BeautifulSoup(html, 'html.parser')
                # Saves the DataFrames in the class
                try:
                    self.odds_tables[soup.text]  = self.get_odds_table(element)
                except:
                    element.click()
                    self.odds_tables[soup.text]  = self.get_odds_table(element)
                    
                self.hist_odds_tables[soup.text] = self.get_hist_odds_table(soup.text, div)
                
                # Closes the table
                element.click()
                div += 1
        
        
        # OTHER FUNCTIONS
    
        def get_odds_table(self, element):
            """ Function to get current odds table """
            
            # Find the table in the page (html format) and convert it to a pandas DataFrame
            table_html = self.game.driver.find_element_by_xpath('//*[@id="odds-data-table"]').get_attribute("innerHTML")
            # Convert html table to DataFrame
            odds_table = pd.read_html(table_html)[0]
            # Format the DataFrame to the desired format
            odds_table.index = odds_table['Bookmakers']
            odds_table = odds_table[odds_table.index.isin(self.game.bookmakers)][self.columns]
            #odds_table = odds_table[:-2]#.dropna(axis=0)
            odds_table = odds_table.apply(pd.to_numeric, errors='ignore')
            # Returns the DataFrame
            return odds_table
            
            
        def get_hist_odds_table(self, value, div_index, min_bs=10):
            """ Returns the historical odds table for the specified european handicap number_of_goals
                filtering by min_bs (by default 10) """
            
            #if (number_of_goals not in self.available_values): return pd.DataFrame()
            
            # Get shape and as a base the odds table
            odds_table = self.odds_tables[value]
            R, C = odds_table.shape
            hist_odds_table = odds_table.copy()
            
            # Iterate through all odds to scrap their respective historical odds
            for i in range(R):
                for j in range(C):
                    # Search for xpath and perform an action to obtain data in the pop-up bubble 
                    XPATH = ('//*[@id="odds-data-table"]/div[%d]/table/tbody/tr[%d]/td[%d]/div'
                              % (div_index, i+1,j+self.td), )[0]
                    
                    # It is either raw text (div) or a link (a)
                    try:    element = self.game.driver.find_element_by_xpath(XPATH)
                    except: 
                        try:    element = self.game.driver.find_element_by_xpath(XPATH[:-3]+'a')
                        except: break
                    
                    # If historical data bubble not available, save only entry
                    try:
                        ActionChains(self.game.driver).move_to_element(element).perform()
                        bubble      = self.game.driver.find_element_by_xpath("//*[@id='tooltiptext']")
                        bubble_data = bubble.get_attribute("innerHTML")
                        data = {}
                        # Convert bubble html code to dictionary with dates as keys and odds as values
                        for date in re.findall(odds_portal_data['date_pattern'], bubble_data):
                            i1 = bubble_data.find(date)
                            i2 = bubble_data[i1:].find('</strong>') + i1
                            key, value = bubble_data[i1:i2].split('  <strong>')
                            data[key]  = value
                        # Assign to each DataFrame cell its respective dictionary
                        hist_odds_table.iloc[i,j] = str(data)
                        
                    except:
                        hist_odds_table.iloc[i,j] = str({self.game.date:odds_table.iloc[i,j]})
                        
            # Returns the DataFramein JSON format
            return hist_odds_table
        

                
                
    
    
    
    
  
