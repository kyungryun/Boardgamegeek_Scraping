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
    conn = pymongo.MongoClient('127.0.0.1',27017)
    db = conn.bggDB
    collection = db.game

    for n in game_list:
        collection.insert(n)
    print("insert %d games complete" % len(game_list))

def create_game_list(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    game_item = soup.select('#row_')
    game_list = []

    for n in game_item:
        rank = n.select('td.collection_rank')[0].text.strip()
        id = n.select('td.collection_objectname a')[0].get('href').split('/')[2]
        game_list.append({ 'game_id' : int(id) , \
                            'game_rank' : rank})

    print("insert DB...")
    insert_game(game_list)

def crawling_game_page(page, last_page):
    page_source = ""
    while 1:
        if page != last_page+1:
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

print("calc last page")
last_page = find_last_page()
print("total pages %d" % last_page)

print("start crawling")
crawling_game_page(page, last_page)
