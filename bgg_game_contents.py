from bs4 import BeautifulSoup
import requests
import re
import pymongo
import lxml

conn = pymongo.MongoClient('127.0.0.1',27017)
db = conn.bggDB
collection = db.gameList

BOARDGAME_URL = "https://boardgamegeek.com/xmlapi2/thing?id=%s?comments=0&stats=1&videos=0"
items = collection.find()
cnt = 0
for item in items:
    xml = requests.get(BOARDGAME_URL%item['id']).text
    soup = BeautifulSoup(xml, 'lxml')

    title = item['title']
    year = item['year']
    weight = soup.find('averageweight')['value']
    average = soup.find('average')['value']
    geekaverage = soup.find('bayesaverage')['value']

    print("%s %d %s %s %s"%(title,year,weight,average,geekaverage))
