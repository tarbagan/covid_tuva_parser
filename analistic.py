# -*- coding: utf8 -*-
"""
Обработчик данных Минздрава РТ
по COVID19
Автор: Иргит В.
"""
import pandas as pd
import json

N = 324537 # на 1 января 2019 г.

file_out = 'covid_tuva.json'
file = 'infection.csv'
df = pd.read_csv(file, encoding="cp1251", error_bad_lines=False, )
df['date'] = pd.to_datetime(df['date'])
df.index = df['date']


def today():
    """Количество инфицированных на сегодня
    last_day - Последняя дата
    today_inf - Количество зарегистрированных случаев на последнюю дату
    yester_day - Дата предыдущих суток
    yesterday_inf - Количество зарегистрированных случаев на предыдущие сутки
    new - Всего новых случаев на текущую и предыдущею дату
    new_pr - Всего новых случаев на текущую и предыдущею дату в процентах
    totalper - Всего инфицированных ко всему населению
    dead - Всего умерших
    min_infection - Стартовое количество инфицированных
    """
    data = df.copy()
    try:
        today_day = data['date'][0].strftime('%d/%m/%y')
        today_inf = int(data['infection'][0])

        yester_day = data['date'][1].strftime('%d/%m/%y')
        yesterday_inf = int(data['infection'][1])

        new = today_inf - yesterday_inf
        new_pr = yesterday_inf * 100 / today_inf
        new_pr = int(new_pr)

        totalper = today_inf * 100 / N
        totalper = round(totalper, 2)

        stat = data.describe()
        dead = stat['dead']['max']
        min_infection = stat['infection']['min']

        return {'last_day': today_day, 'today_inf': today_inf, 'yester_day': yester_day,
                'yesterday_inf': yesterday_inf, 'new': new, 'new_pr': new_pr, 'totalper': totalper,
                'dead': dead, 'min_infection': min_infection}
    except Exception as e:
        return {'error': e}

def rt():
    """Получаем Коэффициент распространения Rt
    rt - Коэффициент распространения Rt
    arr_today - Количество инфицированных за последние 4 дня
    arr_yesterday - Количество инфицированных за предыдущие 4 дня
    rt_all - Коэффициенты распространения Rt на весь период эпидемии
    """
    data = df.copy()
    try:
        last_day = data.index[0].strftime('%d/%m/%y')
        rt_today = data['infection'][0:4].sum() / data['infection'][4:9].sum()
        rt_today = round(rt_today, 1)
        arr_today = [x for x in data['infection'][0:4]]
        arr_yesterday = [x for x in data['infection'][4:8]]
        rt_all = data.groupby(pd.Grouper(key='date', freq='4D')).sum()
        rt_all = rt_all.sort_values(by='date', ascending=False)
        rt_all['Rt'] = rt_all.infection / rt_all.infection.shift(-1)
        rt_all.dropna(inplace=True)
        rt_all = rt_all['Rt'][1:-1]
        rt_all = [round(x,2) for x in rt_all]
        return {'last_day': last_day, 'rt' : rt_today, 'arr_today' : arr_today, 'arr_yesterday': arr_yesterday, 'rt_all': rt_all}
    except Exception as e:
        return {'error': e}

def pcr():
    """Лабораторных исследований ПЦР
    last - всего ПЦР
    yest_pcr - количество ПЦР на предыдущую дату
    new_pcr - количество ПЦР на сутки
    kof_pcr- Охват тестированием населения (официальная метрика)
    arr_seven - данные за семь дней
    per_kof - Процент тестов на количество населения
    per_inf - процент инфицированных в скрининговой группе
    """
    data = df.copy()
    try:
        data.dropna(subset=['lab'], inplace=True)
        per_inf = data['infection'][0] * 100 / data['lab'][0]
        per_inf = round(per_inf, 1)
        last_day = data.index[0].strftime('%d/%m/%y')
        last_pcr = data['lab'][0]
        yest_pcr = data['lab'][1]
        new_pcr = last_pcr - yest_pcr
        seven = data['lab'][0:7]
        arr_seven = [x for x in seven]
        seven = seven.describe()
        kof_pcr = (((seven['max'] - seven['min']) * 100000) / N) / 7
        kof_pcr = int(kof_pcr)
        per_kof = last_pcr * 100 / N
        per_kof = round(per_kof, 1)
        return {'last_day': last_day, 'last_pcr': last_pcr, 'yest_pcr': yest_pcr, 'new_pcr': new_pcr,
                'kof_pcr': kof_pcr, 'arr_seven': arr_seven, 'per_kof' : per_kof, 'per_inf': per_inf}
    except Exception as e:
        return {'error': e}

def rec():
    """Учёт выздоровевших (recovered)
    last_day - Последняя дата
    last_rec - количество на последнюю дату
    all_rec - всего за всё время
    per_rec - соотношение выздоровевших к инфицированным
    mean_stat - среднее количество за всё время
    """
    data = df.copy()
    try:
        last_day = data.index[0].strftime('%d/%m/%y')
        last_rec = data['recovered'][0]
        all_rec = data['recovered'].sum()
        stat = data['recovered'].describe()
        mean_stat =  int(stat['mean'])
        return {'last_day': last_day,'last_rec': last_rec, 'all_rec': all_rec, 'mean_stat': mean_stat}
    except Exception as e:
        return {'error': e}

def news():
    data = df.copy()
    try:
        news = data['news'][0]
        return {'news': news}
    except Exception as e:
        return {'error': e}


today = today()
rt = rt()
pcr = pcr()
rec = rec()
news = news()
data = {'today': today, 'rt': rt, 'pcr': pcr, 'rec': rec, 'news': news}

json_out = json.dumps(data, ensure_ascii=False)
print (json_out)
with open(file_out, 'w', encoding='utf-8') as file:
    file.write(str(json_out))
