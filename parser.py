# -*- coding: utf8 -*-
"""
Парсер новостей с сайта Минздрава, для формирования json и csv
Автор: Иргит Валерий
Версия: 0.1
"""
import requests
from bs4 import BeautifulSoup as bs
import re
import csv


end_news = 145 # макс. кол-во новостей
file = 'infection.csv'

def request_url(url):
    """Получаем страницу"""
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/71.0.3578.98 Safari/537.36'}

    try:
        r = requests.get(url, headers=headers).text
        soup = bs(r, 'html.parser')
        return soup
    except Exception as e:
        print(e)


def gen_pai():
    return [f'https://minzdravtuva.ru/?start={x}' for x in range(1, end_news, 5)]


def get_info(soup):
    """Находим область новостей"""
    return soup.findAll('div', {'itemprop': 'blogPost'})


def clear(str):
    str = re.sub( '\n', '', str)
    str = re.sub( '\t', '', str)
    return str


def zar(text):
    """Количество заражённых"""
    regex = [
        u'выявлено\s(.+?)\sслучаев',
        u'выявлено\s(.+?)\sслучая',
        u'выявлен\s(.+?)\sслучай',
        u'составило\s(.+?)\sбольных',
        u'составило\s(.+?)\sчеловек',
        u'составил\s(.+?)\sчеловек',
        u'зарегистрирован\s(.+?)\sслучай',
        u'зарегистрировано\s(.+?)\sслучаев',
        u'зарегистрировано\s(.+?)\sлабораторно-подтвержденных',
    ]
    match = [re.findall(x, text) for x in regex]
    match = [x for x in match if x]
    match = (match[0] if match else None)
    if match is not None:
        if match[0].isdigit():
            infection = match[0]
            return infection
        else:
            sp = match[0].split()
            if sp[0].isdigit():
                infection = sp[0]
                return infection
            else:
                if sp[0] == 'девять':
                    return 9
                if sp[0] == 'восемь':
                    return 8
                if sp[0] == 'шесть':
                    return 6
    else:
        return None


def isl(text):
    """Количество лаб исследований"""
    regex = [
        u'проведено\s(.+?)\sлабораторных',
    ]
    match = [re.findall(x, text) for x in regex][0]
    if match is not None:
        match = [re.sub(' ', '', x) for x in match if x]
        if match:
            return match[0]
    else:
        return None


def zdor(text):
    """Выписанно здоровых"""
    regex = [
        u'выздоровлением\s(.+?)\sпаци\w',
        u'них\s(.+?)\sсняты',
        u'них\s(.+?)\sвыписаны',
        u'выздоровело\s(.+?)\sчеловек',
    ]
    match = [re.findall(x, text) for x in regex]
    match = [x[0] for x in match if x]
    if not match:
        return None
    else:
        if match[0].isdigit():
            return match[0]


def dead(text):
    """Умерло"""
    regex = [
        u'Зарегистрирован\s(.+?)\sлетальн\w',
        u'Зарегистрирован\s(.+?)\sслучай летальн\w',
        u'Зафиксирован\s(.+?)\sслучай летал\w',
        u'Отмечен\s(.+?)\sлетал\w',
    ]
    match = [re.findall(x, text) for x in regex]
    match = [x[0] for x in match if x]
    if not match:
        return None
    else:
        if match[0] == 'один':
            return 1
        if match[0] == 'два':
            return 2
        if match[0] == 'три':
            return 3



infection_all = []
for url in gen_pai():
    soup = request_url(url)
    for news in get_info(soup):
        title = news.find('h2').text
        title = clear(title)
        date = news.time.attrs['datetime']
        content = news.find('p').text
        content = clear(content)

        if title[0:12] == 'Эпидситуация':
            if content:
                date = date[:10]
                data = {'date': date, 'infection': zar(content), 'lab': isl(content), 'recovered': zdor(content),
                        'dead': dead(content), 'news': content}
                infection_all.append(data)


try:
    csv_columns = ['date', 'infection', 'lab', 'recovered', 'dead', 'news']
    with open(file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in infection_all:
            writer.writerow(data)
except IOError:
    print("I/O error")
