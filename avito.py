# new avito 


def avito_quest(pub_link):
    growing = {}
    for i in starting:
        growing[i] = 'none'
    try:
        print('блять')
        driver = docs.web()
        driver.get(pub_link)
        driver.find_element_by_partial_link_text('Показать').click()
        sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print(soup)
        phone_a = soup.find('a', class_='item-phone-button')
        if phone_a is not None:
            phone_img = phone_a.find('img')
            if phone_img is not None:
                if phone_img.get('src') is not None:
                    search = re.search('data:image/png;base64,(.*)', phone_img.get('src'))
                    if search:
                        imgdata = base64.b64decode(search.group(1))
                        with open('image.png', 'wb') as f:
                            f.write(imgdata)
                            f.close()
                        phone_raw = str(pytesseract.image_to_string(Image.open('image.png')))
                        search = re.search('\s(\d{3})\s', phone_raw)
                        if search:
                            phone_raw = re.sub(' ' + search.group(1) + ' ', ' (' + search.group(1) + ') ', phone_raw)
                        phone_raw = re.sub('—', '-', phone_raw)
                        phone_number = re.sub('\s+', ' ', phone_raw)
                        phone_cheker = re.sub('\D', '', phone_number)
                        if len(phone_cheker) == 11:
                            growing['phone'] = phone_raw
        driver.close()

        rooms_li = soup.find_all('li', class_='item-params-list-item')
        for i in rooms_li:
            if i.find('span') is not None:
                if i.find('span').get_text().strip() == 'Количество комнат:':
                    search = re.search('(\d+)-', i.get_text())
                    if search:
                        growing['rooms'] = search.group(1)

        price_span = soup.find('span', class_='js-item-price')
        if price_span is not None:
            search = re.search('(\d+)', re.sub('\s', '', price_span.get_text().strip()))
            if search:
                growing['price'] = [int(search.group(1)), int(search.group(1)) // 65]

        address_span = soup.find('span', class_='item-address__string')
        if address_span is not None:
            growing['address'] = re.sub('\s+', ' ', address_span.get_text()).strip()

        geo_div = soup.find('div', class_='b-search-map')
        if geo_div is not None:
            if geo_div.get('data-map-lat') is not None and geo_div.get('data-map-lon') is not None:
                growing['geo'] = geo_div.get('data-map-lat') + ',' + geo_div.get('data-map-lon')

        geo_search = re.search('coordinates":{"lat":(.*?),"lng":(.*?)}', str(soup))
        if geo_search:
            growing['geo'] = re.sub('\s', '', geo_search.group(1)) + ',' + re.sub('\s', '', geo_search.group(2))
        metro_span = soup.find('span', class_='item-address-georeferences-item')
        if metro_span is not None:
            metro_st_span = metro_span.find('span', class_='item-address-georeferences-item__content')
            metro_walk_span = metro_span.find('span', class_='item-address-georeferences-item__after')
            metro = ['none', 'none']
            if metro_st_span is not None:
                metro[0] = metro_st_span.get_text().strip()
            if metro_walk_span is not None:
                metro[1] = re.sub('\s+', ' ', metro_walk_span.get_text().strip())
            growing['metro'] = metro

        name_div = soup.find('div', class_='seller-info-name')
        if name_div is not None:
            if name_div.find('a') is not None:
                growing['name'] = re.sub('\s+', ' ', name_div.find('a').get_text()).strip()

        date_raw = soup.find('div', class_='title-info-metadata-item-redesign')
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
                    search = re.search('\d{4}', date_text)
                    if search is None:
                        year = datetime.utcfromtimestamp(stamp).strftime('%Y')
                        modifier += ' ' + year
                    date_text = re.sub(i, modifier, date_text)
            search = re.search(' в \d{2}:\d{2}', date_text)
            pattern = '%d %m %Y'
            if search:
                pattern += ' в %H:%M'
            date_to_stamp = stamper(date_text, pattern)
            if date_to_stamp is not None:
                growing['date'] = date_to_stamp

        search = re.search('https://(.*?)\..*?/', re.sub('www\.', '', pub_link))
        if search:
            growing['site'] = search.group(1).capitalize()

        photo_div = soup.find('div', class_='gallery-img-wrapper')
        if photo_div is not None:
            photo_img = photo_div.find('img')
            if photo_img is not None:
                if photo_img.get('src') is not None:
                    growing['photo'] = 'https:' + photo_img.get('src')
    except IndexError and Exception:
        executive(avito_quest, 1)
    return [pub_link, growing]
