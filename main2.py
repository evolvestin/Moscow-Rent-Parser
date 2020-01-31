import requests
from bs4 import BeautifulSoup
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
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
