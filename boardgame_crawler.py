from bs4 import BeautifulSoup
import requests

page = 1
game = 0
whole_source = ""
while 1:
    if page != 11:
        url = 'https://boardgamegeek.com/browse/boardgame/page/'+ str(page)
        req = requests.get(url)
        whole_source = whole_source + req.text
        page = page + 1
    else:
        break
soup = BeautifulSoup(whole_source, 'html.parser')
game_list = soup.select('td.collection_objectname a')
for n in game_list:
    game = game + 1
    print(n.text.strip())
print(game)
