from bs4 import BeautifulSoup
import requests
import re
import pymongo
import lxml

def get_contents(id):
    xml = requests.get("https://boardgamegeek.com/xmlapi2/thing?id=%s?comments=1&stats=1"%id).text
    soup = BeautifulSoup(xml, 'lxml')

    # game Thumbnail
    thumbnail = ''
    try:
        thumbnail = soup.find('thumbnail').text
    except:
        thumbnail = 'https://cf.geekdo-images.com/micro/img/QZDNfKAPYlXkZg265NxdjgShBXY=/fit-in/64x64/pic1657689.jpg'

    # suggested_numPlayers
    # votes id 3 : Best 2 : Recommended 1 : Not Recommended
    suggested_numPlayers = {}

    # language dependence levels
    # level 0 : No votes
    # level 1 : No necessary in-game text
    # level 2 : Some necessary text - easily memorized or small crib sheet
    # level 3 : Moderate in-game text - needs crib sheet or paste ups
    # level 4 : Extensive use of text - massive conversion needed to be playable
    # level 5 : Unplayable in another language
    language_Dependence = {0:0}
    polls = soup.findAll('poll')

    for poll in polls:
        if poll['name'] == 'suggested_numplayers' and int(poll['totalvotes']) != 0:
            numplayers = poll.findAll('results')
            for numplayer in numplayers:
                votes = numplayer.findAll('result')
                suggested_numPlayers[numplayer['numplayers']] = {
                    1 : int(votes[2]['numvotes']) ,\
                    2 : int(votes[1]['numvotes']) ,\
                    3 : int(votes[0]['numvotes'])}
        if poll['name'] == 'language_dependence' and int(poll['totalvotes']) != 0:
            dependences = poll.findAll('result')
            for dependence in dependences:
                language_Dependence[int(dependence['level'])] = int(dependence['numvotes'])

    # Best , Recommended, NotRecommended Players
    playersRecommended = []
    playersBest = []
    playersNotRecommended = []

    for num in suggested_numPlayers :
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

    # suggested Language Dependence
    suggested_language_Dependence = keys[values.index(max(values))]

    # Num Players
    minPlayer = soup.find('minplayers')['value']
    maxPlayer = soup.find('maxplayers')['value']

    # Playing Time
    minPlayTime = soup.find('minplaytime')['value']
    maxPlayTime = soup.find('maxplaytime')['value']

    # Min Age
    minAge = soup.find('minage')['value']

    # game category, mechanic, family, expansion, designer, artist, publisher
    boardgameCategory = []
    boardgameMechanic = []
    boardgameDesigner = []
    boardgameFamily = []
    boardgameExpansion = []
    boardgameArtist = []
    boardgamePublisher = []

    for eachtag in soup.findAll('link'):
        if eachtag['type'] == 'boardgamecategory':
            boardgameCategory.append(eachtag['id'])
        elif eachtag['type'] == 'boardgamemechanic':
            boardgameMechanic.append(eachtag['id'])
        elif eachtag['type'] == 'boardgamedesigner':
            boardgameDesigner.append(eachtag['id'])
        elif eachtag['type'] == 'boardgamefamily':
            boardgameFamily.append(eachtag['id'])
        elif eachtag['type'] == 'boardgameexpansion':
            try:
                if eachtag['inbound'] == 'true':
                    inbound = True
            except:
                inbound = False
            boardgameExpansion.append({eachtag['id'] : inbound})
        elif eachtag['type'] == 'boardgameArtist':
            boardgameArtist.append(eachtag['id'])
        elif eachtag['type'] == 'boardgamePublisher':
            boardgamePublisher.append(eachtag['id'])

    # group ranks
    # { subgroup name : { rank : bayesaverage } }
    ranks = {}
    for ranking in soup.findAll('rank'):
        ranks[ranking['name']] = {
                    ranking['value'] if ranking['value'].isnumeric() else 'N/A' :
                        ranking['bayesaverage'] if not ranking['bayesaverage'] == 'Not Ranked' else 'N/A'}

    # statistics
    usersrated = soup.find('usersrated')['value']
    average = soup.find('average')['value']
    bayesaverage = soup.find('bayesaverage')['value']
    stddev = soup.find('stddev')['value']
    median = soup.find('median')['value']
    owned = soup.find('owned')['value']
    wishing = soup.find('wishing')['value']

    # weights
    numcomments = soup.find('numcomments')['value']
    numweights = soup.find('numweights')['value']
    averageweight = soup.find('averageweight')['value']

conn = pymongo.MongoClient('127.0.0.1',27017)
db = conn.bggDB
game_page = db.game_page
game_contents = db.game_contents
items = game_page.find()

# get all contents
#hello world
for item in items:
    get_contents(item['id'])
