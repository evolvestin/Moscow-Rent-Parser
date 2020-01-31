import requests
from bs4 import BeautifulSoup
headers = {
  'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
  'accept-encoding':'gzip, deflate, br',
  'accept-language':'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
  'cache-control':'no-cache',
  'dnt': '1',
  'pragma': 'no-cache',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'none',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

session = requests.Session()
session.headers = headers
print(headers)
text = session.get('https://www.avito.ru/moskva/kvartiry/sdam/na_dlitelnyy_srok?user=1')
print(text)
soup = BeautifulSoup(text.text, 'html.parser')
posts_raw = soup.find_all('div', class_='item__line')
posts = []
for i in posts_raw:
    link = i.find('a', class_='snippet-link')
    if link is not None:
      print('https://www.avito.ru' + link.get('href'))
      posts.append('https://www.avito.ru' + link.get('href'))
