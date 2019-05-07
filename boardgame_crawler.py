from bs4 import BeautifulSoup
import requests
import re
import pymongo

conn = pymongo.MongoClient('127.0.0.1',27017)
db = conn.bggDB
collection = db.game

page = 1
game = 0
whole_source = ""
last_page = -1
print("start crawling..")
while 1:
    if page != 10:
        url = 'https://boardgamegeek.com/browse/boardgame/page/'+ str(page)
        req = requests.get(url)
        whole_source = whole_source + req.text
        #if page == 1:
            #soup = BeautifulSoup(whole_source, 'html.parser')
            #last_page = int(re.findall('\d+',soup.select('#main_content div.infobox .fr a')[-1].text)[0])
        page = page + 1
    else:
        break
print("total pages 100")
soup = BeautifulSoup(whole_source, 'html.parser')
game_item = soup.select('#row_')
game_data = []
print("processing....")
for n in game_item:
    rank = n.select('td.collection_rank')[0].text.strip()
    thumbnail = n.select('td.collection_thumbnail img')[0].get('src')
    name = n.select('td.collection_objectname a')[0]
    id = name.get('href').split('/')[2]
    rating = n.select('td.collection_bggrating')
    avgRating = n.select('td.collection_bggrating')[1].text.strip()
    numVoters = n.select('td.collection_bggrating')[2].text.strip()
    game_data.append({ 'game_id' : int(id) , \
                        'game_name' : name.text.strip(),\
                        'game_rank' : rank,\
                        'game_thumbnail' : thumbnail,\
                        'geekRating' : rating[0].text.strip(),\
                        'avgRating' : rating[1].text.strip(),\
                        'numVoters' : rating[2].text.strip()})
print("insert DB....")
for n in game_data:
    collection.insert(n)
print("Complete Insert")
