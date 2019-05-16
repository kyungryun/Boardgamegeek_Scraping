from bs4 import BeautifulSoup
import requests
import re
import pymongo

# Find list page
def find_last_page():
    url = 'https://boardgamegeek.com/browse/boardgame/page/1'
    req = requests.get(url).text
    soup = BeautifulSoup(req, 'html.parser')
    last_page = int(re.findall('\d+',soup.select('#main_content div.infobox .fr a')[-1].text)[0])
    return last_page

# insert to DB without duplicate
def insert_game(list):
    global collection
    for n in list:
        try:
            collection.insert(n)
        except:
            collection.update(
                {'id' : n['id']},
                {'$set' : {'rank' : n['rank']}}
            )

    print("insert %d games complete" % len(game_list))

# parsing list using page_source
# flag 0 : gamepage 1 : gamecategory 2 : gamemechanic
def parsing_list(page_source, flag):
    soup = BeautifulSoup(page_source, 'html.parser')
    list = []
    if flag == 0:
        items = soup.select('#row_')
        for item in items:
            rank = item.select('td.collection_rank')[0].text.strip()
            title = item.select('td.collection_objectname a')[0]
            year = re.findall('\d+', n.select('td.collection_objectname span')[0].text.strip())[0]
            id = title.get('href').split('/')[2]
            list.append({ 'id' : int(id) , \
                                'title' : title.text.strip() , \
                                'year' : int(year),\
                                'rank' : int(rank)})

    elif flag == 1:
        items = soup.find('table', {'class' : 'forum_table'}).findAll('a')
        for item in items:
            id = item['href'].split('/')[2]
            name = item.text.strip()
            list.append({ 'id' : id, 'category' : name} )
    elif flag == 2:
        items = soup.find('table', {'class' : 'forum_table'}).findAll('a')
        for item in items:
            id = item['href'].split('/')[2]
            name = item.text.strip()
            list.append({ 'id' : id, 'mechanic' : name} )

    insert_game(list)
    print("insert DB...")



# crawling game page 1 to last_page
def crawling_game_page(page, last_page):
    page_source = ""
    while 1:
        if page != 2:
            url = 'https://boardgamegeek.com/browse/boardgame/page/'+ str(page)
            req = requests.get(url)
            page_source = page_source + req.text
            if page%10 == 0:
                parsing_list(page_source, 0)
                page_source = ""
            page = page + 1
        else:
            parsing_list(page_source, 0)
            break

def crawling_contents(domain):
    page_source = ""
    url = 'https://boardgamegeek.com/browse/%s'%domain
    req = requests.get(url)
    page_source = page_source + req.text
    soup = BeautifulSoup(page_source, 'html.parser')
    


"""
page = 1
conn = pymongo.MongoClient('127.0.0.1',27017)
db = conn.bggDB
gameList = db.gameList
gameCategories = db.categories
gamemechanic = db.mechanic

last_page = find_last_page()
print("totalgame list pages %d" % last_page)

print("start crawling")
crawling_game_page(page, last_page)
collection.create_index('id', unique=True)
"""
