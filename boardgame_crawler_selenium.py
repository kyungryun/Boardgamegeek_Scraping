from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome('/home/kryun/python_crawler/chromedriver')
driver.implicitly_wait(3)
#driver.get('https://boardgamegeek.com')
#driver.find_element_by_id('login_username').send_keys('username')
#driver.find_element_by_id('login_password').send_keys('password')
#driver.find_element_by_xpath("//div[@class='loginbox']/input").click()

page = 1
game = 0
while 1:
    if page != 11:
        driver.get('https://boardgamegeek.com/browse/boardgame/page/'+str(page))
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        game_list = soup.select('td.collection_objectname a')
        for n in game_list:
            game = game + 1
            print(n.text.strip())
        page = page + 1
    else:
        break
print(game)
