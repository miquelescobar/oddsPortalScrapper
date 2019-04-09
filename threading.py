# Module that contains auxiliar functions and tools


####################################################################################################
############################################## IMPORT ##############################################
####################################################################################################

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime as timer
import oddsPortal
from tools import * #write_json, read_json, get_webdriver, login, clean_game_dict


#%%#################################################################################################
############################################ CONSTANTS #############################################
####################################################################################################

# Define webdriver options
WEBDRIVER = 'chrome'
HEADLESS = True
THREADS = 8
results = []
made = []


#%%#################################################################################################
######################################## TOOLS / FUNCTIONS #########################################
####################################################################################################

def scrap_game(game_url):
    
    print('STARTING PROCESS FOR URL:', game_url)
    game = oddsPortal.Game(game_url, headless=HEADLESS, save=True)
    outputFile = data_dir + game.filename
    results.append(game)
    game_dict = clean_game_dict(game.__dict__)
    write_json(game_dict, outputFile)
    made.append(game_url)
    print('FINISHED PROCESS FOR URL:', game_url)
    
    
#%%#################################################################################################
############################################ MAIN CODE #############################################
####################################################################################################
    

CONTINENT = 'Europe' 
LEAGUE = 'ES1'
    

for season in generate_seasons(2013,2018):
    
    start = timer.now()
    
    urls_dir = '../Storage/Games_URLS/'+CONTINENT+'/'+LEAGUE+'/'+LEAGUE+'_URLS_'+season+'.csv'
    data_dir = '../Storage/Games_Data/'+CONTINENT+'/'+LEAGUE+'/'+LEAGUE+'_Data_'+season+'/'
    
    if season == '2013-2014': games_urls = read_json(urls_dir)[250:]
    else:                     games_urls = read_json(urls_dir)
    to_do = len(games_urls)
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        executor.map(scrap_game, games_urls)
    
    print('\n\nFinished', LEAGUE, season, len(made), 'THREADS within', timer.now()-start)
    print(to_do - len(made), 'THREADS have comitted an error')






