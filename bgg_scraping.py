from bs4 import BeautifulSoup
from multiprocessing import Pool
import requests
import re
import pymongo
import time

page = 1
conn = pymongo.MongoClient('127.0.0.1',27017)
db = conn.bggDB
game_page = db.game_page
game_category = db.game_category
game_mechanic = db.game_mechanic

# Find list page
def find_last_page():
    url = 'https://boardgamegeek.com/browse/boardgame/page/1'
    req = requests.get(url).text
    soup = BeautifulSoup(req, 'html.parser')

    last_page = int(re.findall('\d+',soup.select('#maincontent div.infobox .fr a')[-1].text)[0])
    return last_page

# crawling game page 1 to last_page
def get_game_page(page):
    url = 'https://boardgamegeek.com/browse/boardgame/page/'+ str(page)
    req = requests.get(url).text
    soup = BeautifulSoup(req, 'html.parser')
    list = []
    items = soup.select('#row_')
    for item in items:
        try:
            rank = int(item.select('td.collection_rank')[0].text.strip())
        except:
            rank = 0
        title = item.select('td.collection_objectname a')[0]
        try:
            year = int(re.findall('\d+', item.find('span',{'class' : 'smallerfont dull'}).text)[0])
        except:
            year = 0
        id = title.get('href').split('/')[2]
        list.append({ 'id' : int(id) , \
                            'title' : title.text.strip() , \
                            'year' : year,\
                            'rank' : rank})
    for n in list:
        try:
            game_page.insert(n)
        except:
            game_page.update(
                {'id' : n['id']},
                {'$set' : {'rank' : n['rank']}}
            )

    if game_page.count() % 1000 == 0:
        print("total %d games " % game_page.count() )

# crawling game content
def get_contents(domain):
    page_source = ""
    url = 'https://boardgamegeek.com/browse/%s'%domain
    req = requests.get(url).text
    soup = BeautifulSoup(req, 'html.parser')

    items = soup.find('table', {'class' : 'forum_table'}).findAll('a')
    list = []
    for item in items:
        id = item['href'].split('/')[2]
        name = item.text.strip()
        if domain == 'boardgamecategory':
            list.append({ 'id' : id, 'category' : name} )
        else:
            list.append({ 'id' : id, 'mechanic' : name} )
    for n in list:
        if domain == 'boardgamecategory':
            game_category.insert(n)
        else:
            game_mechanic.insert(n)


if __name__ == '__main__':
    Pool
    if game_category.count() == 0:
        print("game category crawling")
        get_contents('boardgamecategory')

    if game_mechanic.count() == 0:
        print("game mechanic crawling")
        get_contents('boardgamemechanic')

    start_time = time.time()
    last_page = find_last_page()
    print("totalgame list pages %d" % last_page)

    print("game page crawling start %d" % start_time)

    pool = Pool(processes=4)
    pool.map(get_game_page,range(1, last_page+1))

    # create index
    if 'id' not in game_page.index_information():
        game_page.create_index('id',unique=True)
    print(time.time() - start_time)
