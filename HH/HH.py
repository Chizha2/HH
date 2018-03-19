import requests as r # HTTP запросы
import matplotlib.pyplot as p # гистограммы
import statistics
import time
from collections import defaultdict
import progressbar

url = 'https://api.hh.ru/vacancies' # ссылка для работы с вакансиями (из API)
topic = ("machine learning", "data science", "big data", "data analytics") # список тем
money = ("80к-", "80-120к", "120-150к", "150-200к", "200-300к", "300к+") # список диапазонов ЗП
money_data = [0, 0, 0, 0, 0, 0] # количество вакансий
val = {"KZT": 0.1788, "BYR": 29.3039, "EUR": 70.8099, "USD": 57.5043, "UAH": 2.196, "RUR": 1} # курс валют
zps = defaultdict(list)
dead = 0 # индикатор ложной ЗП
d = 0

for i in topic: # по темам словаря
    n = 0 # счетчик вакансий с указанной ЗП
    all_zp = 0 # средняя ЗП по 1 теме
    par = {'text': i} # параметры запроса
    pages = int(r.get(url, par).json()['pages']) # выполнение запроса
    bprog = progressbar.ProgressBar(max_value = pages)
    cprog = 0
    for j in range(pages): # по страницам
        cprog += 1
        par = {'text': i, 'page': j} # параметры запроса
        while d == 0:
            try:
                m = r.get(url, par).json()['items'] # выполнение запроса, декодирование json и переход к вакансиям
                d = 1
            except:
                print("САЙТ УПАЛ")
        d = 0

        for k in m: # переберает вакансии текущей страницы
            if k['salary'] == None: # есть ли общие данные по зарплате
                continue # прерывание
            s = k['salary'] # записываем общие данные по зарплате в переменную s
            if s["currency"] != "RUR" and s["currency"] != "KZT" and s["currency"] != "BYR" and s["currency"] != "EUR" and s["currency"] != "USD" and s["currency"] != "UAH": # проверяем валюту
                continue # прерывание

            if s["from"] != None and s["to"] != None: # если только конечная ЗП
                zp = (s['from'] + s['to']) / 2 * val[s["currency"]] # увеличение суммы ЗП по 1 теме
                n += 1 # вакансий с указанной ЗП
            elif s["from"] != None and s["to"] == None: # если только начальная ЗП
                if s["from"] * val[s["currency"]] >= 300000: # если ЗП более 300000
                    zp = 300000 # ложная ЗП
                    dead = 1 # индикатор
                else: # иначе
                    continue # прерывание
            else: # иначе
                if s["to"] * val[s["currency"]] < 80000: # если ЗП до 80000
                    zp = 1 # значение для 
                    dead = 1 # ложная ЗП
                else: # иначе
                    continue # прерывание

            if zp < 80000: # 1 диапазон
                money_data[0] += 1 # + вакансия
            elif zp >= 80000 and zp < 120000: # 2 диапазон
                money_data[1] += 1 # + вакансия
            elif zp >= 120000 and zp < 150000: # 3 диапазон
                money_data[2] += 1 # + вакансия
            elif zp >= 150000 and zp < 200000: # 4 диапазон
                money_data[3] += 1 # + вакансия
            elif zp >= 200000 and zp < 300000: # 5 диапазон
                money_data[4] += 1 # + вакансия
            elif zp >= 300000: # 6 диапазон
                money_data[5] += 1 # + вакансия

            if dead: # если ложная ЗП
                dead = 0 # обнуление индикатора
            else: # иначе
                if 'area' in k:
                    zps[k["area"]["name"]].append(zp)
        bprog.update(cprog)

bprog.finish()
for i in zps:
    zps[i] = statistics.median(zps[i])

    
p.Figure()
thismanager = p.get_current_fig_manager()
thismanager.window.wm_iconbitmap('favicon.ico')
p.xlabel("Диапазон ЗП в рублях")
p.ylabel("Количество вакансий") 
p.title("Распределение количества вакансий по диапазонам ЗП")
p.gcf().canvas.set_window_title('Распределение количества вакансий по диапазонам ЗП')
p.barh(money, money_data)
p.show()

thismanager = p.get_current_fig_manager()
thismanager.window.wm_iconbitmap('favicon.ico')
p.xlabel("Средняя ЗП в рублях")
p.ylabel("Название региона") 
p.title("Средние ЗП по регионам")
p.gcf().subplots_adjust(left = 0.2)
p.gcf().canvas.set_window_title('Средние ЗП по регионам')
p.barh(list(zps.keys()), list(zps.values()))
p.show()
# изменение