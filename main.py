'''
Documentation
Written By: Thor Truelson, NFP Games and Entertianment Division
Date: July 2022

Thanks To: 
Bird, Steven, Edward Loper and Ewan Klein (2009), Natural Language Processing with Python. O’Reilly Media Inc.



Dependencies:
Python 3.8.8
beautifulsoup4
googlesearch-python-extended

nltk
requests
htmldate
'''


#imports
from pickle import NONE
from pkg_resources import iter_entry_points
import googlesearch

import argparse
import toolConstants
import os
import sys

import pandas
import datetime

import bs4
import requests
import nltk
nltk.download('punkt')
from htmldate import find_date


"""
creates the parser that
"""
def createProgramParser():
	parser = argparse.ArgumentParser(description= "Get Injury Data for specific person, usually MLB player")

	### add the flags
	parser.add_argument('Players', help= "String or file containing the names of the players to search")

	parser.add_argument('-s',default= "Injury",help = "Search term for the web search")

	parser.add_argument('-o',  default= "output.xlsx", help="filename of output" )

	dateNow = datetime.datetime.now()
	parser.add_argument('-y', default = dateNow.year, help= "Look up injuries starting this year", type = int)

	parser.add_argument('-x', default= 5, help="Number of search hits that will be used per month", type = int)
	### how many articles per month?

	parser.add_argument('-silent', default= False, help= "Do not show the other text")

	return parser




'''
	Take a players parameter. This could either be 
	a String of players or some file. If it is 
	a .csv file or .xlsx file scan for some entries 
	that are under players or somewhat like that 
	keywords are defined in toolConstants.py. 
	
	Returns a list of string referencing these players. 
'''
def formatPlayers(players):
	#currentDirectory = os.getcwd()

	if not os.path.exists(players):
		print("Players: " + str(players.split(",")))
		return players.split(",")
	
	extension = os.path.splitext(players)[1]

	wb = None
	if extension == ".csv":
		wb = pandas.read_csv(players)
	elif extension == ".xlsx":
		wb = pandas.read_excel(players)
	else:
		# Doesn't need to handle the other just throw an error
		print("Uploaded players file has extension that is not .xlsx or .csv exiting:")
		quit(1)

	### read the players column
	for col in wb.columns:
		colTokens = col.lower().strip(" ").split(" ")
		
		### this checks if the col has something in common with the words for players
		isPlayerColumn = any(check in colTokens for check in toolConstants.regexForPlayers)
		if isPlayerColumn:
			return list(wb[col])

	print("No Players Column for input, exiting program")
	quit(1)

def formatQuery(curQuery, fromDate, toDate):
   
	dateRange = f"&tbs=cdr%3A1%2Ccd_min%3A{fromDate.month}%2F{fromDate.day}%2F{fromDate.year}%2Ccd_max%3A{toDate.month}%2F{toDate.day}%2F{toDate.year}&tbm="

	return curQuery + dateRange


##TODO
def findArticles(player, args): 
	if int(args.y) < 2000:
		print("Not searching past 2000, rerun with different parameters")
		quit(1)


	### Query string for search (is "Player_name" injury by default)
	query = player + " " + str(args.s)

	### add date range functionality
	dateNow = datetime.datetime.now()
	nowDay, nowMonth, nowYear = dateNow.day,dateNow.month, dateNow.year
	itrDay, itrMonth, itrYear = nowDay, nowMonth, nowYear

	numHits = args.x
	
	### return list
	retSearches = set()

	while itrYear >= int(args.y): 

		### handles the generation of the data ranges
		toDate = datetime.datetime(itrYear, itrMonth, itrDay)
		itrYear, itrMonth, itrDay = itrYear - 1 if itrMonth == 1 else itrYear, 12 if itrMonth == 1 else itrMonth -1, 28 if itrMonth == 3 else 30
		fromDate = datetime.datetime(itrYear, itrMonth, itrDay)
		
		### handles the amount of searches left, 
		### approximate is 29 days difference for each period, there is a better method for sure but IDC
		tempYear = itrYear

		if itrMonth == 1:
			itrMonth = 11
			itrDay = 30
			itrYear -= 1

		
		## make the searches
		finalQuery = formatQuery(query, fromDate, toDate)
	
		searches = googlesearch.search(finalQuery, num_results = numHits)
	
	
		for search in searches:
			retSearches.add((search, tempYear, fromDate, toDate))
	return retSearches

'''
Get the text from the article we are gonna reformat the UTF-8 inclsuive string 
into sraight ASCII and do some pre processing in order to reduce NLP overhead in 
following functions
'''
def getArticleText(URL):
	response = None
	try: 
		response = requests.get(URL, timeout = 5.0)
	except:
		return "", ""

	soup = bs4.BeautifulSoup(response.text, 'html.parser')

	time = "Unknown"
	for t in soup.findAll('time'):
		if t.has_attr('datetime'):
			time = t


	### Here is the human readable text of the website now to preprocess it
	textWriting = soup.get_text()
	textWriting = textWriting.encode("ascii","ignore").decode().replace("\n"," ")
	textWriting = textWriting.lower()
	
	return textWriting, time

def extractQuote(sentence, word): 

	center = sentence.index(word)
	L = len(sentence)
	words = []

	
	l,r = center, center + 1
	while ((l > 0) and (abs(l-center) <= 2)):
		words.insert(0,sentence[l])
		l -= 1 
	while ((r < L) and (abs(r-center) <= 2)):
		words.append(sentence[r])
		r += 1

	return " ".join(words)

def extractInjury(headlineWords):
	tokenWords = nltk.pos_tag(headlineWords)

	adjs = ['JJ','JJR','JJS','VBG']
	injList = []
	for i,(word, id) in enumerate(tokenWords):
		if word in toolConstants.injuryWords and id == "NN":
			
			leftWord = ""
			if i != 0 and tokenWords[i-1][1] in adjs:
				leftWord = tokenWords[i-1][0]
			
			rightWord = ""
			if i != (len(tokenWords) -1) and tokenWords[i+1][1] in adjs: 
				rightWord = tokenWords[i+1][0]

			injList.append((word, (leftWord + " " + word + " " + rightWord).strip()))
	### tags for adj are jj jjr jjs vbg

	if "tommy" in headlineWords and "john" in headlineWords:
		injList.append("tommy john", headlineWords)


	return injList


'''
Return the injury in the headline
'''
def processArticle(articleURL, player, fromDate):
	headlineWords = articleURL.lower().split('/')
	headlineWords = headlineWords[-2] if headlineWords[-1] == "" else headlineWords[-1]
	headlineWords = headlineWords.rsplit('.',1)[0].split('-')
	
	records = set()

	intersectedName = [word for word in nltk.word_tokenize(player.lower()) if word in headlineWords]
	if intersectedName == []:
		return records


	intersectedInj = extractInjury(headlineWords)

	###back is an issue want back + anotherInjuryWord for it
	date = "Unknown"
	try:
		date = find_date(articleURL)
		for inj, injPhrase in intersectedInj:
			newInjRecord = toolConstants.InjuryRecord(player, inj, injPhrase, articleURL, date)
			records.add(newInjRecord)
		return records
	except:
		date = fromDate.strftime('%Y-%m-%d')
		for inj, injPhrase in intersectedInj:
			newInjRecord = toolConstants.InjuryRecord(player, inj, injPhrase, articleURL, date)
			records.add(newInjRecord)
		return records
		

def processArticles(articlesURL, player):
	injSet = set()
	for (articleURL,year, fromDate, toDate) in articlesURL:
		for injRecord in processArticle(articleURL, player, fromDate):
			injSet.add(injRecord)
	return injSet


'''
def processInjuries(injuries): 
	injuriesFinal = set()
	for inj in injuries:
		###TODO check
		hi = 1+1


	return injuriesFinal
'''




def scrapePlayer(player, args):
	##SHOULD BE LIST OF INJURY DICTS
	#injuries = toolConstants.outputDictTemplate

	### first do a websearch for a player
	articlesURL = findArticles(player, args)

	### We are going to first search for the text
	### then find the injuries in the text
	injList = processArticles(articlesURL, player)
	
	### this should be a speed up for the dataframe creation but might 
	### offload this into the injuries final logic if it essentially
	### a duplicate load
	retList = []
	for inj in injList: 
		dict_data_new  = inj.turnToDict()		
		retList.append(dict_data_new)
	
	return retList




'''
This is the driver that proceeds as follows
1) function scapes for player injuries
2) verify uniqueness of injuries 
3) Write each injury to the output file in some standard TBD 

TODO
'''
def scrapeDriver(players, args):
	dictList = []

	### write the injuries to the dict
	for player in players: 
		dictList.append(scrapePlayer(player, args))
	
	
	###because of multiple injuries we must flatten
	flattenList = [elem for sublist in dictList for elem in sublist]
	
	
	###convert dict into dataframe
	df = pandas.DataFrame.from_dict(flattenList)

	###write the data frame to an .xlsx file
	df.to_excel('./' + args.o, sheet_name= "Injuries", index = False)

	print("Done writing to file : ./" + args.o + " Check for a sheet named Injuries")
	return 


if __name__ == '__main__':
	
	#parse the options, documentation should be apparent
	print(toolConstants.programSpiel)
	
	parser = createProgramParser()
	args = parser.parse_args()
	print(args)
	### now we handle the input if it is a file
	players = formatPlayers(args.Players)

	### now we scrape the internet for the players
	scrapedInjuires = scrapeDriver(players, args)

	quit(0)




