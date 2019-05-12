from bs4 import BeautifulSoup
import requests
import re
import pymongo
import lxml

conn = pymongo.MongoClient('127.0.0.1',27017)
db = conn.bggDB
collection = db.gameList

items = collection.find()
cnt = 0
game_contents = []

def get_contents(id):
    xml = requests.get("https://boardgamegeek.com/xmlapi2/thing?id=%s?comments=0&stats=1&videos=0"%id).text
    soup = BeautifulSoup(xml, 'lxml')

    #game Thumbnail
    thumbnail = soup.find('thumbnail').text

    polls = soup.findAll('poll')
    #suggested_numPlayers
    # votes id 3 : Best 2 : Recommended 1 : Not Recommended
    suggested_numPlayers = {}

    #language dependence levels
    #level 1 : No necessary in-game text
    #level 2 : Some necessary text - easily memorized or small crib sheet
    #level 3 : Moderate in-game text - needs crib sheet or paste ups
    #level 4 : Extensive use of text - massive conversion needed to be playable
    #level 5 : Unplayable in another language
    language_Dependence = {}

    for poll in polls:
        if poll['name'] == 'suggested_numplayers':
            numplayers = poll.findAll('results')
            for numplayer in numplayers:
                votes = numplayer.findAll('result')
                suggested_numPlayers[numplayer['numplayers']] = {
                    1 : int(votes[2]['numvotes']) ,\
                    2 : int(votes[1]['numvotes']) ,\
                    3 : int(votes[0]['numvotes'])}
        if poll['name'] == 'language_dependence':
            dependences = poll.findAll('result')
            for dependence in dependences:
                language_Dependence[int(dependence['level'])] = int(dependence['numvotes'])

    #Best , Recommended, NotRecommended Players
    playersRecommended = []
    playersBest = []
    playersNotRecommended = []

    for num in suggested_numPlayers:
        values = list(suggested_numPlayers[num].values())
        keys = list(suggested_numPlayers[num].keys())
        maxVotes = keys[values.index(max(values))]

        if maxVotes == 1:
            playersNotRecommended.append(num)
        elif maxVotes == 2:
            playersRecommended.append(num)
        else:
            playersBest.append(num)

    keys = list(language_Dependence.keys())
    values = list(language_Dependence.values())

    #suggested Language Dependence
    suggested_language_Dependence = keys[values.index(max(values))]

    #Num Players
    minPlayer = soup.find('minplayers')['value']
    maxPlayer = soup.find('maxplayers')['value']

    #Playing Time
    minPlayTime = soup.find('minplaytime')['value']
    maxPlayTime = soup.find('maxplaytime')['value']

    minAge = soup.find('minage')['value']

    #game category, mechanic
    boardgameCategory = []
    boardgameMechanic = []
    tag = soup.findAll('tag')
    for eachtag in tag:
        if eachtag['type'] == 'boardgamecategory':
            boardgameCategory.append(eachtag['id'])
        elif eachtag['type'] == 'boardgamemechanic':
            boardgameMechanic.append(eachtag['id'])

    #group ranks
    ranks = soup.find('ranks')
    print(ranks)
    
    #ratings
    usersrated = soup.find('usersrated')['value']
    average = soup.find('average')['value']
    bayesaverage = soup.find('bayesaverage')['value']

    #weights
    numweights = soup.find('numweights')['value']
    averageweight = soup.find('averageweight')['value']

collection = db.gameContents
get_contents(174430)

#for n in game_contents:
    #collection.insert(n)
