'OddsPortal Scrapper' ReadMe (Version 1.0, Europe)


Countries: Spain, England, France, Germany, Italy, Portugal, Netherlands.
Leagues: First Division in every country.
Training data seasons: from 2007/2008 to 2017/2018.
Testing seasons: from 2018/2019 to -.

Bet types: Correct Result (1X2), Over/Under, Draw No Bet, European Handicap.

Data will be stored as a pandas (python module) DataFrame in files database.json and backup.json, directory /Storage.
The data frame will contain the following data:
	- Date as a datetime class ('Date')
	- Country as a string of length 3 ('Country')
	- Division as an integer ('Division')
	- Home Team as a string ('Home_Team')
	- Away Team as a string ('Away_Team')
	- Home Goals as an integer ('FT_Home_Goals')
	- Away Goals as an integer ('FT_Away_Goals')
	- Final Result as a character ('FTR', options=['H','D','A']
	- Half Time Home Goals as an integer ('HT_Home_Goals')
	- Half Time Away Goals as an integer ('HT_Away_Goals')
	- Half Time Result as a character ('HTR', options=['H','D','A']
	- OddsPortal Url as a string ('OP_URL')
	- Odd as a float ( str (Bookmaker_Name + '_' Bet_Type_Abbreviation) )
	- Bet Type number of Bookmakers ( str(Bet_Type_Abbreviation) + '_BKS' )


Following Bet_Type_Abbreviation's used (n takes any integer value):

    Correct Result (1X2) = HDA 
	Final Time 1 = FTH
	Final Time X = FTD
	Final Time 2 = FTA
	Half Time 1 = HTH
	Half Time X = HTD
	Half Time 2 = HTA

    Over/Under = OU
	Over n.5 goals =  On5
	Under n.5 goals =  Un5

    Draw No Bet = DNB
	Draw No Bet Home Win = DNBH
	Draw No Bet Away Win = DNBA

    European Handicap = EH
	Europen Handicap n = EHn
	European Handicap -n = EHnegn





