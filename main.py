import os
import re
import docs
import base64
import objects
import _thread
import gspread
import requests
import pytesseract
from time import sleep
from telebot import types
from bs4 import BeautifulSoup
from datetime import datetime
from objects import bold, code, italic, stamper

stamp1 = objects.time_now()
objects.environmental_files()
client3 = gspread.service_account('person3.json')
client4 = gspread.service_account('person4.json')
used3 = client3.open('Moscow-Rent').worksheet('main')
used4 = client4.open('Moscow-Rent').worksheet('main')
used_array = used3.col_values(1)

keyboard = types.InlineKeyboardMarkup(row_width=2)
buttons = [types.InlineKeyboardButton(text='✅', callback_data='post'),
           types.InlineKeyboardButton(text='👀', callback_data='viewed')]
starting = ['rooms', 'price', 'address', 'geo', 'metro', 'name', 'phone', 'date', 'site', 'photo']
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'}
pytesseract.pytesseract.tesseract_cmd = docs.tesseract_path
calendar_list = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12'
}
calendar_list_short = {
    'янв': '01',
    'фев': '02',
    'мар': '03',
    'апр': '04',
    'мая': '05',
    'июн': '06',
    'июл': '07',
    'авг': '08',
    'сен': '09',
    'окт': '10',
    'ноя': '11',
    'дек': '12'
}
idMe = 396978030
idAndre = 470292601
keyboard.add(*buttons)
idMain = -1001402644636
idBack = -1001220481011
# ====================================================================================
Auth = objects.AuthCentre(os.environ['TOKEN'], -1001320247347)
bot = Auth.start_main_bot('non-async')
create_image = open('image.png', 'w')
executive = Auth.thread_exec
Auth.start_message(stamp1)
create_image.close()
# ====================================================================================


def move_quest(pub_link):
    req = requests.get(pub_link, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')

    growing = {}
    for i in starting:
        growing[i] = 'none'

    rooms_li = soup.find_all('li', class_='object-info__details-table_property')
    if rooms_li is not None:
        for i in rooms_li:
            if i.find('div', attrs={'title': 'Количество комнат'}) is not None:
                rooms = i.find('div', class_='object-info__details-table_property_value')
                if rooms is not None:
                    growing['rooms'] = rooms.get_text()

    price = soup.find('span', class_='block-price_main-price-value js-price-main-value')
    if price is not None:
        search = re.search(r'(\d+)', re.sub(r'\s', '', price.get_text().strip()))
        if search:
            growing['price'] = [int(search.group(1)), int(search.group(1)) // 65]

    address_div = soup.find('div', class_='short-address')
    if address_div is not None:
        address = address_div.find_all(['a', 'span'])
        for i in address:
            if growing['address'] != 'none':
                growing['address'] += ', ' + i.get_text()
            else:
                growing['address'] = re.sub(r'г\. ', '', i.get_text())

    geo_search = re.search(r'YaMaps\.coords=\[(.*?)\];', str(soup))
    if geo_search:
        growing['geo'] = re.sub(r'\s', '', geo_search.group(1))

    metro_raw = soup.find('ul', class_='geo-block__block-distance')
    if metro_raw is not None:
        metro = ['none', 'none']
        metro_station = metro_raw.find('li', 'geo-block__block-distance_metro')
        metro_walk = metro_raw.find('li', 'geo-block__block-distance_walk-time')
        if metro_station is not None:
            metro[0] = metro_station.get_text().strip()
        if metro_walk is not None:
            metro[1] = metro_walk.get_text().strip()
        growing['metro'] = metro

    if soup.find('div', class_='block-user'):
        name = soup.find('a', class_='block-user__name')
        if name is not None:
            growing['name'] = re.sub(r'\s+', ' ', name.get_text().strip())

    search = re.search(r'https://move\.ru/objects/(.*)', pub_link)
    if search:
        phone_link = 'https://move.ru/objects_print/printing/' + search.group(1)
        phone_req = requests.get(phone_link, headers=headers)
        phone_soup = BeautifulSoup(phone_req.text, 'html.parser')
        phone = phone_soup.find('div', class_='phone')
        if phone is not None:
            phone_raw = phone.get_text()
            if phone_raw.startswith('7') and len(phone_raw) == 11:
                growing['phone'] = '+' + phone_raw[0] + ' (' + phone_raw[1] + phone_raw[2] + phone_raw[3] + ') ' + \
                    phone_raw[4] + phone_raw[5] + phone_raw[6] + '-' + phone_raw[7] + phone_raw[8] + '-' + \
                    phone_raw[9] + phone_raw[10]
            else:
                growing['phone'] = phone_raw

    date_raw = soup.find('li', class_='block-date__time block-date__li')
    if date_raw is not None:
        date_text = date_raw.get_text()
        stamp = int(datetime.now().timestamp())
        if date_raw.get_text().find('вчера') != -1:
            stamp -= 24 * 60 * 60
            day = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%d')
            month = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%m')
            year = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%Y')
            date_text = re.sub('вчера', day + ' ' + month + ' ' + year, date_text)
        elif date_raw.get_text().find('сегодня') != -1:
            day = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%d')
            month = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%m')
            year = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%Y')
            date_text = re.sub('сегодня', day + ' ' + month + ' ' + year, date_text)
        else:
            for i in calendar_list:
                date_text = re.sub(i, calendar_list.get(i), date_text)
        search = re.search(r' в \d{2}:\d{2}', date_text)
        pattern = '%d %m %Y'
        if search:
            pattern += ' в %H:%M'
        date_to_stamp = stamper(date_text, pattern)
        if date_to_stamp is not None:
            growing['date'] = date_to_stamp

    search = re.search(r'https://(.*?)\..*?/', pub_link)
    if search:
        growing['site'] = search.group(1).capitalize()

    photo = soup.find_all('img', attrs={'alt': '', 'itemprop': 'contentUrl'})
    if photo is not None:
        for i in photo:
            growing['photo'] = i.get('src')
    return [pub_link, growing]


def sob_quest(pub_link):
    req = requests.get(pub_link, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    roomer = ''

    growing = {}
    for i in starting:
        growing[i] = 'none'

    price = soup.find('p', class_='text-price')
    if price is not None:
        search = re.search(r'(\d+)', re.sub(r'\s', '', price.get_text().strip()))
        if search:
            growing['price'] = [int(search.group(1)), int(search.group(1)) // 65]

    address_div = soup.find('div', class_='flex-two-equals')
    if address_div is not None:
        address_array = address_div.find_all('a', class_='black-link')
        growing['address'] = 'Москва'
        for i in address_array:
            if roomer != '':
                roomer += ', ' + i.get_text()
            else:
                roomer += i.get_text()
        if roomer != '':
            growing['address'] += ', ' + roomer

    rooms_div = soup.find('div', class_='adv-page-title')
    if rooms_div is not None:
        rooms = rooms_div.find('h1')
        if rooms is not None:
            rooms_raw = re.sub(r'Сдается|квартира|' + roomer, '', rooms.get_text()).strip()
            search = re.search(r'(\d+)-комнатная', rooms_raw)
            if search:
                growing['rooms'] = search.group(1)

    geo_search = re.search(r'coords: \[(.*?)\],', str(soup))
    if geo_search:
        growing['geo'] = re.sub(r'\s', '', geo_search.group(1))

    metro_raw = soup.find('p', class_='subway-link')
    if metro_raw is not None:
        metro = ['none', 'none']
        metro_station = metro_raw.find('a', attrs={'target': '_blank'})
        metro_walk = metro_raw.find('span', class_='text-cm')
        if metro_station is not None:
            metro[0] = metro_station.get_text().strip()
        if metro_walk is not None:
            metro[1] = re.sub(r'\(|\)|пешком', '', metro_walk.get_text()).strip()
        growing['metro'] = metro

    phone_div = soup.find('div', class_='phone-show-visible')
    if phone_div is not None:
        growing['phone'] = phone_div.get_text().strip()

    date_raw = soup.find('p', class_='text-date')
    if date_raw is not None:
        date_text = date_raw.get_text()
        stamp = int(datetime.now().timestamp())
        if date_raw.get_text().find('вчера') != -1:
            stamp -= 24 * 60 * 60
            day = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%d')
            month = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%m')
            year = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%Y')
            date_text = re.sub('вчера', day + ' ' + month + ' ' + year, date_text)
        elif date_raw.get_text().find('сегодня') != -1:
            day = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%d')
            month = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%m')
            year = datetime.utcfromtimestamp(int(stamp + 3 * 60 * 60)).strftime('%Y')
            date_text = re.sub('сегодня', day + ' ' + month + ' ' + year, date_text)
        else:
            for i in calendar_list:
                date_text = re.sub(i, calendar_list.get(i), date_text)
        search = re.search(r' в \d{2}:\d{2}', date_text)
        pattern = '%d %m %Y'
        if search:
            pattern += ' в %H:%M'
        date_to_stamp = stamper(re.sub('Дата публикации:', '', date_text).strip(), pattern)
        if date_to_stamp is not None:
            growing['date'] = date_to_stamp

    search = re.search(r'https://(.*?)\..*?/', pub_link)
    if search:
        growing['site'] = search.group(1).capitalize()

    photo_raw = soup.find('div', id='fotoramaCard')
    if photo_raw is not None:
        photo = photo_raw.find('a')
        if photo is not None:
            growing['photo'] = 'https:' + photo.get('data-thumb')
    return [pub_link, growing]


def kvartirant_quest(pub_link):
    req = requests.get(pub_link, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')

    growing = {}
    for i in starting:
        growing[i] = 'none'

    rooms_divs = soup.find_all('div', class_='obj-info')
    if rooms_divs is not None:
        for i in rooms_divs:
            rooms = i.find('h3')
            if rooms is not None:
                price = rooms.find('span')
                if price is not None:
                    search = re.search(r'(\d+)', re.sub(r'\s', '', price.get_text().strip()))
                    if search:
                        growing['price'] = [int(search.group(1)), int(search.group(1)) // 65]
                rooms_raw = re.sub(r'Сдам|квартиру|' + '', '', rooms.get_text()).strip()
                search = re.search(r'(\d+)-комнат', rooms_raw)
                if search:
                    growing['rooms'] = search.group(1)

    address_p = soup.find('p', class_='gray_a')
    if address_p is not None:
        address = address_p.find('b')
        if address is not None:
            if address.get_text() == 'На карте:':
                modify_address = re.sub('На карте:', '', address_p.get_text()).strip()
                growing['address'] = re.sub('.*?Москва', 'Москва', modify_address).strip()

    geo_search = re.search(r'center: \[(.*?)\]', str(soup))
    if geo_search:
        growing['geo'] = re.sub(r'\s', '', geo_search.group(1))

    metro_raw = soup.find_all('div', class_='col-xs-12 obj-info')
    for i in metro_raw:
        metro_spans = i.find_all('span')
        metro = ['none', 'none']
        for g in metro_spans:
            metro_b = g.find('b')
            if metro_b is not None:
                search = re.search('Метро', metro_b.get_text())
                search_rent = re.search('ПОСУТОЧНАЯ АРЕНДА', metro_b.get_text())
                if search:
                    metro_a = g.find_all('a')
                    for a in metro_a:
                        if metro[0] == 'none':
                            metro[0] = a.get_text().strip()
                        else:
                            metro[0] += ', ' + a.get_text().strip()
                if search_rent:
                    growing['address'] += '\n🎟 ' + metro_b.get_text().strip().capitalize()
            if g.get('class') == ['gray_a']:
                if g.find('i') is not None:
                    metro[1] = re.sub('/пешком', '', g.get_text()).strip()
        growing['metro'] = metro

    phone_raw = soup.find('div', class_='obj-contact')
    if phone_raw is not None:
        phone = phone_raw.find('span', class_='red')
        if phone is not None:
            phone_text = ''
            search = re.findall(r'document\.write\(\'(.*?)\'\)', phone.get_text())
            for i in search:
                phone_text += i
            growing['phone'] = phone_text.strip()
        search = re.search(r'(.*?)\|.*', phone_raw.get_text().strip())
        if search:
            growing['name'] = re.sub('if.*', '', search.group(1)).strip().capitalize()

    date_raw = soup.find('div', class_='obj-data')
    if date_raw is not None:
        date_text = re.sub('Добавлено:', '', date_raw.get_text())
        stamp = int(datetime.now().timestamp())
        if date_raw.get_text().find('1 день назад') != -1:
            stamp -= 24 * 60 * 60
            day = datetime.utcfromtimestamp(stamp).strftime('%d')
            month = datetime.utcfromtimestamp(stamp).strftime('%m')
            year = datetime.utcfromtimestamp(stamp).strftime('%Y')
            date_text = re.sub('1 день назад', day + ' ' + month + ' ' + year, date_text)
        elif date_raw.get_text().find('Сегодня') != -1:
            day = datetime.utcfromtimestamp(stamp).strftime('%d')
            month = datetime.utcfromtimestamp(stamp).strftime('%m')
            year = datetime.utcfromtimestamp(stamp).strftime('%Y')
            date_text = re.sub('Сегодня', day + ' ' + month + ' ' + year, date_text)
        else:
            for i in calendar_list:
                date_text = re.sub(i, calendar_list.get(i), date_text)
        search = re.search(r' \d{2}:\d{2}', date_text)
        pattern = '%d %m %Y'
        if search:
            pattern += ' %H:%M'
        date_to_stamp = stamper(date_text, pattern)
        if date_to_stamp is not None:
            growing['date'] = date_to_stamp

    search = re.search(r'https://(.*?)\..*?/', re.sub(r'www\.', '', pub_link))
    if search:
        growing['site'] = search.group(1).capitalize()

    photo = soup.find('ul', class_='bxSlider')
    if photo is not None:
        photo_img = photo.find('img')
        if photo_img is not None:
            if photo_img.get('src') != '/images/no_photo.png':
                growing['photo'] = 'https://www.kvartirant.ru' + photo_img.get('src')
    return [pub_link, growing]


def domofond_quest(pub_link):
    req = requests.get(pub_link, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')

    growing = {}
    for i in starting:
        growing[i] = 'none'

    rooms_div = soup.find('div', class_=re.compile('^detail-information__wrapper'))
    if rooms_div is not None:
        rooms_divs = rooms_div.find_all('div', class_=re.compile('^detail-information__row'))
        for i in rooms_divs:
            if i.get_text().startswith('Комнаты:'):
                growing['rooms'] = re.sub('Комнаты:', '', i.get_text()).strip()
            if i.get_text().startswith('Цена:'):
                search = re.search(r'(\d+)', re.sub(r'\s', '', i.get_text().strip()))
                if search:
                    growing['price'] = [int(search.group(1)), int(search.group(1)) // 65]
            if i.get_text().startswith('Дата публикации объявления:'):
                date_to_stamp = stamper(re.sub('Дата публикации объявления:', '', i.get_text()).strip(), '%d/%m/%Y')
                growing['date'] = date_to_stamp

    address_a = soup.find('a', attrs={'data-scroll-to-id': '#item-location'})
    if address_a is not None:
        address = address_a.get_text().strip()
        if address.endswith('Москва'):
            address = re.sub(', Москва', '', address)
        if address.startswith('Москва'):
            address = address
        else:
            address = 'Москва, ' + address
        growing['address'] = address.strip()

    geo_search = re.search('"location":{"longitude":(.*?),"latitude":(.*?)}', str(soup))
    if geo_search:
        growing['geo'] = re.sub(r'\s', '', geo_search.group(2)) + ',' + re.sub(r'\s', '', geo_search.group(1))

    metro_raw = soup.find('div', class_=re.compile('^information__metro'))
    if metro_raw is not None:
        metro = ['none', 'none']
        metro[0] = metro_raw.get_text()[1:]
        search_km = re.search(r'.*\s(\d+\.\d+\sкм)', metro[0])
        search_m = re.search(r'.*\s(\d+\sм)', metro[0])
        if search_km:
            metro[0] = re.sub(search_km.group(1), '', metro[0]).strip()
            metro[1] = search_km.group(1).strip()
        if search_m:
            metro[0] = re.sub(search_m.group(1), '', metro[0]).strip()
            metro[1] = search_m.group(1).strip()
        growing['metro'] = metro

    name_h3 = soup.find('h3', class_=re.compile('^saller-information__title'))
    if name_h3 is not None:
        if name_h3.get_text().strip() != 'Пользователь':
            growing['name'] = name_h3.get_text().strip()

    try:
        driver = docs.web()
        driver.get(pub_link)
        for i in driver.find_elements_by_tag_name('button'):
            if 'showNumber' in i.get_attribute('class'):
                i.click()
        sleep(2)
        phone_soup = BeautifulSoup(driver.page_source, 'html.parser')
        phone_a = phone_soup.find('a', class_=re.compile('^show-number-button__link'))
        if phone_a is not None:
            phone_raw = phone_a.get_text().strip()
            if re.sub(r'\D', '', phone_raw).startswith('7') and len(re.sub(r'\D', '', phone_raw)) == 11:
                phone_raw = re.sub(r'\D', '', phone_raw)
                growing['phone'] = '+' + phone_raw[0] + ' (' + phone_raw[1] + phone_raw[2] + phone_raw[3] + ') ' + \
                                   phone_raw[4] + phone_raw[5] + phone_raw[6] + '-' + \
                                   phone_raw[7] + phone_raw[8] + '-' + phone_raw[9] + phone_raw[10]
            else:
                growing['phone'] = phone_raw
        driver.close()
    except IndexError and Exception:
        objects.printer('Вылет domofond извлечения номера')

    search = re.search(r'https://(.*?)\..*?/', re.sub(r'www\.', '', pub_link))
    if search:
        growing['site'] = search.group(1).capitalize()

    search = re.search('"openGraphImageUrl":"(.*?)"', str(soup))
    if search:
        growing['photo'] = search.group(1)
    return [pub_link, growing]


def cian_quest(pub_link):
    req = requests.get(pub_link, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')

    growing = {}
    for i in starting:
        growing[i] = 'none'

    rooms_div = soup.find('h1', attrs={'data-name': 'OfferTitle'})
    if rooms_div is not None:
        search = re.search(r'(\d+)-комн.', rooms_div.get_text())
        search_studio = re.search('Студия', rooms_div.get_text())
        if search:
            growing['rooms'] = search.group(1)
        if search_studio:
            growing['rooms'] = '1'

    price_span = soup.find('span', attrs={'itemprop': 'price'})
    if price_span is not None:
        search = re.search(r'(\d+)', re.sub(r'\s', '', price_span.get_text().strip()))
        if search:
            growing['price'] = [int(search.group(1)), int(search.group(1)) // 65]

    address_a = soup.find('address')
    if address_a is not None:
        growing['address'] = re.sub('На карте', '', address_a.get_text()).strip()

    geo_search = re.search('coordinates":{"lat":(.*?),"lng":(.*?)}', str(soup))
    if geo_search:
        growing['geo'] = re.sub(r'\s', '', geo_search.group(1)) + ',' + re.sub(r'\s', '', geo_search.group(2))

    metro_raw = soup.find('li', attrs={'data-name': 'renderUnderground'})
    if metro_raw is not None:
        metro = ['none', 'none']
        metro_a = metro_raw.find('a')
        metro_span = metro_raw.find('span')
        if metro_a is not None:
            metro[0] = metro_a.get_text().strip()
        if metro_span is not None:
            metro[1] = re.sub('пешком|⋅', '', metro_span.get_text()).strip()
        growing['metro'] = metro

    phone = soup.find('a', class_=re.compile('.*?-phone-.*'))
    if phone is not None:
        phone_raw = phone.get_text().strip()
        search = re.search(r'\s(\d{3})\s', phone_raw)
        if search:
            phone_raw = re.sub(' ' + search.group(1) + ' ', ' (' + search.group(1) + ') ', phone_raw)
        growing['phone'] = phone_raw

    date_raw = soup.find('div', attrs={'data-name': 'OfferAdded'})
    if date_raw is not None:
        date_text = re.sub(',', '', date_raw.get_text())
        stamp = int(datetime.now().timestamp())
        if date_raw.get_text().find('вчера') != -1:
            stamp -= 24 * 60 * 60
            day = datetime.utcfromtimestamp(stamp).strftime('%d')
            month = datetime.utcfromtimestamp(stamp).strftime('%m')
            year = datetime.utcfromtimestamp(stamp).strftime('%Y')
            date_text = re.sub('вчера', day + ' ' + month + ' ' + year, date_text)
        elif date_raw.get_text().find('сегодня') != -1:
            day = datetime.utcfromtimestamp(stamp).strftime('%d')
            month = datetime.utcfromtimestamp(stamp).strftime('%m')
            year = datetime.utcfromtimestamp(stamp).strftime('%Y')
            date_text = re.sub('сегодня', day + ' ' + month + ' ' + year, date_text)
        else:
            for i in calendar_list_short:
                date_text = re.sub(i, calendar_list_short.get(i), date_text)
        search = re.search(r' \d{2}:\d{2}', date_text)
        pattern = '%d %m %Y'
        if search:
            pattern += ' %H:%M'
        date_to_stamp = stamper(date_text, pattern)
        if date_to_stamp is not None:
            growing['date'] = date_to_stamp

    search = re.search(r'https://(.*?)\..*?/', re.sub(r'www\.', '', pub_link))
    if search:
        growing['site'] = search.group(1).capitalize()

    photo_meta = soup.find('meta', attrs={'name': 'twitter:image'})
    if photo_meta is not None:
        if photo_meta.get('content') is not None:
            growing['photo'] = photo_meta.get('content')
    return [pub_link, growing]


def irr_quest(pub_link):
    req = requests.get(pub_link, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')

    growing = {}
    for i in starting:
        growing[i] = 'none'

    rooms_span = soup.find('span', class_='productPage__characteristicsItemValue')
    if rooms_span is not None:
        growing['rooms'] = rooms_span.get_text().strip()

    price_div = soup.find('div', class_='productPage__price')
    if price_div is not None:
        search = re.search(r'(\d+)', re.sub(r'\s', '', price_div.get_text().strip()))
        if search:
            growing['price'] = [int(search.group(1)), int(search.group(1)) // 65]

    address_div = soup.find('div', class_='js-scrollToMap')
    if address_div is not None:
        growing['address'] = re.sub(r'\s+', ' ', address_div.get_text()).strip()

    geo_div = soup.find('div', class_='js-productPageMap')
    if geo_div is not None:
        if geo_div.get('data-map-info') is not None:
            geo_search = re.search('{"lat":"(.*?)","lng":"(.*?)",', geo_div.get('data-map-info'))
            if geo_search:
                growing['geo'] = re.sub(r'\s', '', geo_search.group(1)) + ',' + re.sub(r'\s', '', geo_search.group(2))

    geo_search = re.search('coordinates":{"lat":(.*?),"lng":(.*?)}', str(soup))
    if geo_search:
        growing['geo'] = re.sub(r'\s', '', geo_search.group(1)) + ',' + re.sub(r'\s', '', geo_search.group(2))

    phone_input = soup.find('input', attrs={'name': 'phoneBase64'})
    if phone_input is not None:
        if phone_input.get('value') is not None:
            try:
                phone = base64.standard_b64decode(phone_input.get('value'))
                growing['phone'] = phone.decode('utf-8')
            except IndexError and Exception:
                objects.printer('Вылет irr.ru извлечения номера')

    date_raw = soup.find('div', class_='productPage__createDate')
    if date_raw is not None:
        date_text = re.sub(',', '', date_raw.get_text()).strip()
        stamp = int(datetime.now().timestamp())
        if date_raw.get_text().find('вчера') != -1:
            stamp -= 24 * 60 * 60
            day = datetime.utcfromtimestamp(stamp).strftime('%d')
            month = datetime.utcfromtimestamp(stamp).strftime('%m')
            year = datetime.utcfromtimestamp(stamp).strftime('%Y')
            date_text = re.sub('вчера', day + ' ' + month + ' ' + year, date_text)
        elif date_raw.get_text().find('сегодня') != -1:
            day = datetime.utcfromtimestamp(stamp).strftime('%d')
            month = datetime.utcfromtimestamp(stamp).strftime('%m')
            year = datetime.utcfromtimestamp(stamp).strftime('%Y')
            date_text = re.sub('сегодня', day + ' ' + month + ' ' + year, date_text)
        else:
            for i in calendar_list:
                modifier = calendar_list.get(i)
                search = re.search(r'\d{4}', date_text)
                if search is None:
                    year = datetime.utcfromtimestamp(stamp).strftime('%Y')
                    modifier += ' ' + year
                date_text = re.sub(i, modifier, date_text)
        search = re.search(r' \d{2}:\d{2}', date_text)
        pattern = '%d %m %Y'
        if search:
            pattern += ' %H:%M'
        date_to_stamp = stamper(date_text, pattern)
        if date_to_stamp is not None:
            growing['date'] = date_to_stamp

    search = re.search(r'https://(.*?)\..*?/', re.sub(r'www\.', '', pub_link))
    if search:
        growing['site'] = search.group(1).capitalize()

    photo_meta = soup.find('meta', attrs={'itemprop': 'image'})
    if photo_meta is not None:
        if photo_meta.get('content') is not None:
            growing['photo'] = photo_meta.get('content')
    return [pub_link, growing]


def former(growing, kind, pub_link):
    text = '🏢 Свежая '
    if growing['rooms'] != 'none':
        if growing['rooms'] == '1':
            text += 'Однушка '
        elif growing['rooms'] == '2':
            text += 'Двушка '
        elif growing['rooms'] == '3':
            text += 'Трёшка '
        else:
            text += growing['rooms'] + '-х комнатная '
    if growing['price'] != 'none':
        text += 'за ' + str(growing['price'][0]) + '₽ (' + str(growing['price'][1]) + '$)🍒\n'
    if growing['address'] != 'none':
        text += '🗺 ' + growing['address'] + '\n'
    text = bold(text)
    if growing['metro'] != 'none':
        if growing['metro'][0] != 'none':
            text += bold('🚇 ' + growing['metro'][0])
            if growing['metro'][1] != 'none':
                text += italic(' 🚶' + growing['metro'][1])
            text += '\n'
    if growing['name'] != 'none' or growing['phone'] != 'none':
        text += bold('\n📔 Контакты:\n')
        if growing['phone'] != 'none':
            text += italic(growing['phone'])
        if growing['name'] != 'none':
            text += italic(' (' + growing['name'] + ')')
        text += '\n'
    if growing['date'] != 'none':
        text += bold('⏱ Размещено:\n')
        stamp = growing['date']
        day = datetime.utcfromtimestamp(stamp).strftime('%d')
        month = datetime.utcfromtimestamp(stamp).strftime('%m')
        year = datetime.utcfromtimestamp(stamp).strftime('%Y')
        hours = datetime.utcfromtimestamp(stamp).strftime('%H')
        minutes = datetime.utcfromtimestamp(stamp).strftime('%M')
        text += italic(str(day) + '.' + str(month) + '.' + str(year))
        if str(hours) != '00' and str(minutes) != '00':
            text += italic(' в ' + str(hours) + ':' + str(minutes))
        if growing['site'] != 'none':
            text += italic(', ' + growing['site'])
        text += '\n'
    if growing['photo'] != 'none':
        text += '\n<a href="' + growing['photo'] + '">📷 Фото</a>\n'
    else:
        text += '\n📷 <a href="http://i.piccy.info/i9/d54e0fe23cde2f29e1bdac9383549194/1580247525/56511/1359385/' \
            'BD97F41E_45D9_4992_9485_385F3B18898C.jpg">Фото отсутсвуют</a>\n'

    if kind == 'MainChannel':
        keys = None
        if growing['price'] != 'none' and growing['address'] != 'none' and \
                growing['geo'] != 'none' and growing['phone'] != 'none':
            text += '\n📍 <a href="http://maps.yandex.ru/?text=' + growing['geo'] + '">Карта Yandex</a>\n'
            text += '📍 <a href="https://www.google.ru/maps/place/' + growing['geo'] + '">Карта Google</a>\n'
            text += '\n🔎 <a href="' + pub_link + '">Источник</a>\n'
        else:
            text = pub_link
    elif kind == 'zhopa':
        keys = None
        text += code('-------------------\n')
        if growing['geo'].lower() != 'none':
            text += '📍http://maps.yandex.ru/?text=' + growing['geo'] + '\n'
            text += '📍https://www.google.ru/maps/place/' + growing['geo'] + '\n'
        text += '🔎' + pub_link + '🔎\n'
        text += code('-------------------\n')
    else:
        keys = None
        if growing['price'] != 'none' and growing['address'] != 'none' and \
                growing['geo'] != 'none' and growing['phone'] != 'none':
            text += '\n📍 <a href="http://maps.yandex.ru/?text=' + growing['geo'] + '">Карта Yandex</a>\n'
            text += '📍 <a href="https://www.google.ru/maps/place/' + growing['geo'] + '">Карта Google</a>\n'
            text += '\n🔎 <a href="' + pub_link + '">Источник</a>\n'
        else:
            text = pub_link
    return [text, keys]


def searcher(link):
    site_search = re.search('(move.ru|sob.ru|kvartirant.ru|domofond.ru|cian.ru|irr.ru)', link)
    if site_search:
        if site_search.group(1) == 'move.ru':
            post = move_quest(link)
        elif site_search.group(1) == 'sob.ru':
            post = sob_quest(link)
        elif site_search.group(1) == 'kvartirant.ru':
            post = kvartirant_quest(link)
        elif site_search.group(1) == 'domofond.ru':
            post = domofond_quest(link)
        elif site_search.group(1) == 'cian.ru':
            post = cian_quest(link)
        elif site_search.group(1) == 'irr.ru':
            post = irr_quest(link)
        else:
            post = None
    else:
        post = None
    return post


def poster(id_forward, array, pub_link):
    if array[0] is not None:
        if array[0] != pub_link:
            bot.send_message(id_forward, array[0], reply_markup=array[1],
                             parse_mode='HTML', disable_web_page_preview=False)
        else:
            bot.send_message(-1001320247347, 'Что-то пошло не так:\n' + pub_link, parse_mode='HTML',
                             disable_web_page_preview=False)
    else:
        if id_forward != idMain:
            send = id_forward
        else:
            send = -1001320247347
        bot.send_message(send, 'Что-то пошло не так:\n' + pub_link, parse_mode='HTML', disable_web_page_preview=False)


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    try:
        if call.data == 'post':
            search = re.search('🔎(.*?)🔎', call.message.text)
            if search:
                post = searcher(search.group(1))
                if post is not None:
                    poster(idMain, former(post[1], 'MainChannel', post[0]), post[0])
                    text = call.message.text + code('\n✅ опубликован ✅')
                    bot.edit_message_text(chat_id=call.message.chat.id, text=text, message_id=call.message.message_id,
                                          reply_markup=None, parse_mode='HTML', disable_web_page_preview=False)
                else:
                    Auth.send_json(str(call.message), 'callbacks', code('Ссылка какая-то не та'))
            else:
                Auth.send_json(str(call.message), 'callbacks', code('Не нашел в посте ссылку на вакансию'))

        elif call.data == 'viewed':
            text = call.message.text + code('\n👀 просмотрен 👀')
            bot.edit_message_text(chat_id=call.message.chat.id, text=text, message_id=call.message.message_id,
                                  reply_markup=None, parse_mode='HTML', disable_web_page_preview=False)
    except IndexError and Exception:
        executive(str(call))


@bot.message_handler(func=lambda message: message.text)
def repeat_all_messages(message):
    try:
        if message.chat.id == idMe or message.chat.id == idAndre:
            post = searcher(message.text)
            if post is not None:
                poster(message.chat.id, former(post[1], 'Private', post[0]), post[0])
            elif message.text.startswith('/base'):
                doc = open('log.txt', 'rt')
                bot.send_document(message.chat.id, doc)
                doc.close()
            else:
                bot.send_message(message.chat.id, bold('ссылка не подошла'), parse_mode='HTML')
    except IndexError and Exception:
        executive(str(message))


def inserter3(posts, quest):
    global used3
    global client3
    global used_array
    for i in posts:
        if i not in used_array:
            try:
                used3.insert_row([i], 1)
            except IndexError and Exception:
                client3 = gspread.service_account('person3.json')
                used3 = client3.open('Moscow-Rent').worksheet('main')
                used3.insert_row([i], 1)
            used_array.insert(0, i)
            post = quest(i)
            poster(idBack, former(post[1], 'Back', post[0]), post[0])
            objects.printer(i + ' сделано')
            sleep(4)


def inserter4(posts, quest):
    global used4
    global client4
    global used_array
    for i in posts:
        if i not in used_array:
            try:
                used4.insert_row([i], 1)
            except IndexError and Exception:
                client4 = gspread.service_account('person4.json')
                used4 = client4.open('Moscow-Rent').worksheet('main')
                used4.insert_row([i], 1)
            used_array.insert(0, i)
            post = quest(i)
            poster(idBack, former(post[1], 'Back', post[0]), post[0])
            objects.printer(i + ' сделано')
            sleep(5)


def move_checker():
    while True:
        try:
            sleep(1)
            text = requests.get('https://move.ru/arenda_kvartir/ot_sobstvennika/?limit=40', headers=headers)
            soup = BeautifulSoup(text.text, 'html.parser')
            posts_raw = soup.find_all('div', class_='search-item move-object')
            posts = []
            for i in posts_raw:
                link = i.find('a', class_='search-item__title-link')
                if link is not None:
                    posts.append('https:' + link.get('href'))
            inserter3(posts, move_quest)
        except IndexError and Exception:
            executive()


def sob_checker():
    while True:
        try:
            sleep(1)
            text = requests.get('https://sob.ru/arenda-kvartir-moskva-bez-posrednikov?rent_type[]=2', headers=headers)
            soup = BeautifulSoup(text.text, 'html.parser')
            posts_raw = soup.find_all('div', class_='adv-card-title')
            posts = []
            for i in posts_raw:
                link = i.find('a', class_='title-adv')
                if link is not None:
                    if link.get('href').startswith('//sob.ru'):
                        posts.append('https:' + link.get('href'))
            inserter3(posts, sob_quest)
        except IndexError and Exception:
            executive()


def kvartirant_checker():
    while True:
        try:
            sleep(1)
            text = requests.get('https://www.kvartirant.ru/bez_posrednikov/Moskva/sniat-kvartiru/'
                                '?komnat[]=1&komnat[]=2&komnat[]=3&komnat[]=4', headers=headers)
            soup = BeautifulSoup(text.text, 'html.parser')
            posts_raw = soup.find_all('div', class_='obj-info')
            posts = []
            for i in posts_raw:
                link = i.find('a', class_='red')
                if link is not None:
                    posts.append('https://www.kvartirant.ru' + link.get('href'))
            inserter3(posts, kvartirant_quest)
        except IndexError and Exception:
            executive()


def domofond_checker():
    while True:
        try:
            sleep(1)
            text = requests.get('https://www.domofond.ru/arenda-kvartiry-moskva-c3584'
                                '?RentalRate=Month&PrivateListingType=PrivateOwner&SortOrder=Newest', headers=headers)
            soup = BeautifulSoup(text.text, 'html.parser')
            posts_raw = soup.find_all('a', class_=True)
            posts = []
            for i in posts_raw:
                class_list = i.get('class')
                for g in class_list:
                    search = g.find('long-item')
                    if search != -1:
                        posts.append('https://www.domofond.ru' + i.get('href'))
            inserter4(posts, domofond_quest)
        except IndexError and Exception:
            executive()


def cian_checker():
    while True:
        try:
            sleep(1)
            text = requests.get('https://www.cian.ru/snyat-kvartiru-bez-posrednikov/', headers=headers)
            soup = BeautifulSoup(text.text, 'html.parser')
            posts_raw = soup.find_all('a', class_=True)
            posts = []
            for i in posts_raw:
                class_list = i.get('class')
                for g in class_list:
                    search = g.find('--header--')
                    if search != -1:
                        posts.append(i.get('href'))
            inserter4(posts, cian_quest)
        except IndexError and Exception:
            executive()


def irr_checker():
    while True:
        try:
            sleep(1)
            text = requests.get('https://irr.ru/real-estate/rent/sort/date_sort:desc/', headers=headers)
            soup = BeautifulSoup(text.text, 'html.parser')
            posts_raw = soup.find_all('div', class_='listing__item')
            posts = []
            for i in posts_raw:
                link = i.find('a', class_='listing__itemTitle')
                if link is not None:
                    posts.append(link.get('href'))
            inserter4(posts, irr_quest)
        except IndexError and Exception:
            executive()


def telegram_polling():
    try:
        bot.polling(none_stop=True, timeout=60)
    except IndexError and Exception:
        bot.stop_polling()
        sleep(1)
        telegram_polling()


if __name__ == '__main__':
    gain = [domofond_checker, irr_checker, cian_checker, kvartirant_checker, sob_checker, move_checker]
    for thread_element in gain:
        thread_id = _thread.start_new_thread(thread_element, ())
    telegram_polling()
