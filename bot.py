import re
import telebot
from selenium import webdriver
from time import sleep
from datetime import datetime
import os

token = '617835554:AAHTqC39hgIGOSvaGEqrr8wDCGArB5EZwpA'
bot = telebot.TeleBot(token)
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
# huila

stamp1 = int(datetime.now().timestamp())
driver.get("https://www.domofond.ru/2-komnatnaya-kvartira-na-prodazhu-moskva-1803330801")
#driver.find_element_by_class_name('sc-cJSrbW iElBmz').click()
for i in driver.find_elements_by_tag_name('button'):
    if 'showNumber' in i.get_attribute('class'):
        i.click()
sleep(2)
search = re.search('tel:(.+?)"', str(driver.page_source))
if search:
    text = search.group(1) + '\n'
else:
    text = '[]\n'
driver.close()
stamp2 = int(datetime.now().timestamp())
text += str(stamp2 - stamp1)
bot.send_message(396978030, text, parse_mode='HTML')
print(stamp2 - stamp1)
