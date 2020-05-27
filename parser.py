# -*- coding: utf8 -*-
"""
Парсер новостей с сайта минздрава, для формирования json
Автор: Иргит Валерий
Версия: 0.1
"""
import requests
from bs4 import BeautifulSoup as bs
import re
import csv
import json


end_news = 150
file = 'infection.csv'
file_kog = 'koguun.json'

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
    return [f'https://minzdravtuva.ru/?start={x}' for x in range(0, end_news, 5)]


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
        u'Выявлено\s(.+?)\случаев',
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
        u'зарегистрировано\s(.+?)\sслучая смерти'
    ]
    match = [re.findall(x, text) for x in regex]
    match = [x[0] for x in match if x]

    if not match:
        return None
    else:
        if match[0].isdigit():
            return match[0]
        elif match[0] == 'один':
            return 1
        elif match[0] == 'два':
            return 2
        elif match[0] == 'три':
            return 3
        elif match == 'четыре':
            return 4
        else:
            return None

def kog(text):
    """Парсим данные по кожуунам"""
    koguun_all = []
    etalon = [{'name': 'Ак-Довурак', 'population': '14118'},
              {'name': 'Улуг-Хемский кожуун', 'population': '19398'},
              {'name': 'Кызыл', 'population': '108070'},
              {'name': 'Чаа-Хольский кожуун', 'population': '6521'},
              {'name': 'Тес-Хемский кожуун', 'population': '9394'},
              {'name': 'Дзун-Хемчикский кожуун', 'population': '20973'},
              {'name': 'Сут-Хольский кожуун', 'population': '8660'},
              {'name': 'Кызылский кожуун', 'population': '23678'},
              {'name': 'Барун-Хемчикский кожуун', 'population': '12337'},
              {'name': 'Монгун-Тайгинский кожуун', 'population': '6249'},
              {'name': 'Овюрский кожуун', 'population': '8029'},
              {'name': 'Тандинский кожуун', 'population': '13498'},
              {'name': 'Чеди-Хольский кожуун', 'population': '7963'},
              {'name': 'Каа-Хемский кожуун', 'population': '12720'},
              {'name': 'Тере-Хольский кожуун', 'population': '1830'},
              {'name': 'Эрзинский кожуун', 'population': '8528'},
              {'name': 'Пий-Хемский кожуун', 'population': '11135'},
              {'name': 'Бай-Тайгинский кожуун', 'population': '12395'},
              {'name': 'Тоджинский кожуун', 'population': '6123'}]

    regex_start = [{'id': num, 'name': x['name'][:6]} for num, x in enumerate(etalon)]
    regex = [{'id': x['id'], 'regex': u'{}(\w*)\s(\D)\s(\d*)'.format(x['name'])} for x in regex_start]
    match = [(re.findall(x['regex'], text), x['id']) for x in regex]
    for x in match:
        if x[0]:
            kogun = etalon[x[1]]
            data = [[n for n in x if n.isdigit()] for x in x[0]][0]
            kogun['infection'] = data[0]
            if kogun['name'] != 'Кызыл':
                koguun_all.append(kogun)
    return koguun_all


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

                #print (kog(content))


try:
    csv_columns = ['date', 'infection', 'lab', 'recovered', 'dead', 'news']
    with open(file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in infection_all:
            writer.writerow(data)
except IOError:
    print("I/O error")


