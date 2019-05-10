from bs4 import BeautifulSoup
import requests
import re
import pymongo

def find_last_page():
    url = 'https://boardgamegeek.com/browse/boardgame/page/1'
    req = requests.get(url).text
    soup = BeautifulSoup(req, 'html.parser')
    last_page = int(re.findall('\d+',soup.select('#main_content div.infobox .fr a')[-1].text)[0])
    return last_page

def insert_game(game_list):
    global collection
    for n in game_list:
        try:
            collection.insert(n)
        except:
            collection.update(
                {'id' : n['id']},
                {'$set' : {'rank' : n['rank']}}
            )
    print("insert %d games complete" % len(game_list))

def create_game_list(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    game_item = soup.select('#row_')
    game_list = []

    for n in game_item:
        rank = n.select('td.collection_rank')[0].text.strip()
        title = n.select('td.collection_objectname a')[0]
        year = re.findall('\d+', n.select('td.collection_objectname span')[0].text.strip())[0]
        id = title.get('href').split('/')[2]
        game_list.append({ 'id' : int(id) , \
                            'title' : title.text.strip() , \
                            'year' : int(year),\
                            'rank' : int(rank)})

    print("insert DB...")
    insert_game(game_list)

def crawling_game_page(page, last_page):
    page_source = ""
    while 1:
        if page != 2:
            url = 'https://boardgamegeek.com/browse/boardgame/page/'+ str(page)
            req = requests.get(url)
            page_source = page_source + req.text
            if page%10 == 0:
                create_game_list(page_source)
                page_source = ""
            page = page + 1
        else:
            create_game_list(page_source)
            break

page = 1
conn = pymongo.MongoClient('127.0.0.1',27017)
db = conn.bggDB
collection = db.gameList

last_page = find_last_page()
print("total pages %d" % last_page)

print("start crawling")
crawling_game_page(page, last_page)
collection.create_index('id', unique=True)
