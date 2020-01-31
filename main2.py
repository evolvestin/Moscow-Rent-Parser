import requests
from bs4 import BeautifulSoup
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
print(headers)
text = requests.get('https://www.avito.ru/moskva/kvartiry/sdam/na_dlitelnyy_srok?user=1', headers=headers)
print(text)
soup = BeautifulSoup(text.text, 'html.parser')
posts_raw = soup.find_all('div', class_='item__line')
posts = []
for i in posts_raw:
    link = i.find('a', class_='snippet-link')
    if link is not None:
      print('https://www.avito.ru' + link.get('href'))
      posts.append('https://www.avito.ru' + link.get('href'))
