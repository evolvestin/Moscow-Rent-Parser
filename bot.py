import re
from selenium import webdriver
from time import sleep
from datetime import datetime
import os

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)


stamp1 = int(datetime.now().timestamp())
driver.get("https://www.domofond.ru/1-komnatnaya-kvartira-v-arendu-moskva-2085427441")
#driver.find_element_by_class_name('sc-cJSrbW iElBmz').click()
for i in driver.find_elements_by_tag_name('button'):
    if 'showNumber' in i.get_attribute('class'):
        i.click()
sleep(2)
search = re.search('tel:(.+?)"', str(driver.page_source))
if search:
    print(search.group(1))
driver.close()
stamp2 = int(datetime.now().timestamp())
print(stamp2 - stamp1)
