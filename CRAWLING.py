import requests as rq
import time
from bs4 import BeautifulSoup as bs
import re
import datetime
import pandas as pd
import random
from tqdm.notebook import tqdm
import API
import os


def ID_to_sid(ID, tag):
    snapshot = rq.get(f"https://www.fow.lol/find/kr/{ID}-{tag}").text
    soup = bs(snapshot, 'html.parser')
    cover = soup.find('div', id='content-container')
    sid_line = str(cover.find('div', "fbtn lv"))

    sid_re = re.compile(r'(data\-sid=\")(\d*)')
    sid = re.findall(sid_re, sid_line)[0][1]
    return sid


def html(sid, timestamp=int(time.time())):
    return rq.get(f'https://www.fow.lol/api/gamesmore?region=kr&sid={sid}&ts={timestamp}&type=solo&champ=0').text


def parsing(text):
    games_re = re.compile(r'<div class=\"gameDetail hidden\" data-game-id="\d*">\r\n</div>')
    games = re.split(games_re, text)

    return games


def next_timestamp(crawl_list):
    return int(re.findall(r'\d+', crawl_list)[0])


def timestringTotimestamp(time_string):
    element = re.findall(r'\d+', time_string)
    t = int(element[3])
    if re.findall(r'후', time_string):
        if t == 12:
            clock = element[3]
        else:
            clock = f'{int(element[3]) + 12}'
    else:
        if t == 12:
            clock = f'{int(element[3]) - 12}'
        else:
            clock = element[3]
    reorganize = element[0] + '-' + element[1] + '-' + element[2] + ' ' + clock + ':' + element[4] + ':' + element[5]
    return datetime.datetime.strptime(reorganize, '%Y-%m-%d %H:%M:%S').timestamp()


def crawl_to_dict(game):
    soup = bs(game, 'html.parser')
    dict = {}

    dict['win'] = soup.find('div')['class'][1]
    dict['champ'] = soup.find('div', None).find('img')['alt']
    dict['level'] = int(soup.find('div', None).text.strip('\n'))

    dict['kill'] = int(soup.find('span', 'k_string').text)
    dict['death'] = int(soup.find('span', 'd_string').text)
    dict['assist'] = int(soup.find('span', 'a_string').text)
    try:
        dict['kill_engagement'] = float(soup.find('div', tipsy="킬 관여율").text.strip('%'))
    except:
        dict['kill_engagement'] = None

    spells = soup.find_all('img', {'src': re.compile(r'.+spell.+')})
    dict['spell_d'] = spells[0]['tipsy']
    dict['spell_f'] = spells[1]['tipsy']

    perks = soup.find_all('img', {'src': re.compile(r'.+perk.+')})
    dict['perk_main'] = re.findall(r'[^<]\w+[^>]', perks[0]['tipsy'])[0].strip()
    dict['perk_sub'] = re.findall(r'[^<]\w+[^>]', perks[1]['tipsy'])[0].strip()
    dict['position'] = soup.find('img', {'src': re.compile(r'.+pos.+')})['alt']

    items = soup.find_all('img', {re.compile(r'.+item.+')})
    item = []
    dict['shoes'] = None
    dict['ward'] = '투명 와드'
    for i in items:
        temp = i['alt']
        if temp in ['장화', '약간 신비한 신발', '마법사의 신발', '명석함의 아이오니아 장화', '광전사의 군화', '서풍', '헤르메스의 발걸음', '판금 장화', '신속의 장화',
                    '공생형 밑창', '하나 된 영혼', '신속행진', '핏빛 명석함', '건메탈 군화', '주문투척자의 신발', '무장 진격', '사슬끈 분쇄자', '영원한 전진']:
            dict['shoes'] = temp
        elif temp in ['망원형 개조', '예언자의 렌즈', '투명 와드']:
            dict['ward'] = temp
        else:
            item.append(temp)
    dict['item'] = ', '.join(item)

    elseinfo = re.findall(r'\d+(?:[.,]\d+)?', soup.find_all('div')[-8].text)
    dict['cs'] = int(elseinfo[0])
    dict['cs_per_minute'] = float(elseinfo[1])
    dict['gold'] = int(elseinfo[2].replace(',', ''))

    sightinfo = re.findall(r'\d+', soup.find_all('div')[-6]['tipsy'])
    dict['sight_score'] = int(sightinfo[0])
    dict['controll_ward'] = int(sightinfo[1])
    dict['place_ward'] = int(sightinfo[2])
    dict['destroy_ward'] = int(sightinfo[3])

    timeinfo = soup.find_all('div')[-4]
    dict['playtime'] = timeinfo.find_all('div')[0].text
    time = re.findall(r'\d+\. \d+\. \d+\. 오[전|후] \d+:\d+:\d+', timeinfo.find_all('span', 'tipsy_live')[0]['tipsy'])
    dict['start'] = int(timestringTotimestamp(time[0]))
    dict['end'] = int(timestringTotimestamp(time[1]))

    return dict


def ID_to_data(ID, tag, max_page):
    try:
        sid = ID_to_sid(ID, tag)
    except:
        return pd.DataFrame()
    game_info = pd.DataFrame()

    pbar = tqdm(range(max_page),
                total=max_page,
                desc=f'Crawling [{ID}] #{tag}',
                leave=True,
                position=0
                )

    for order in pbar:
        if order == 0:
            data = html(sid)
        elif (order != 0) & (next_page_ts == None):
            break
        else:
            time.sleep(random.uniform(0.5, 1))
            data = html(sid, next_page_ts)
        list = parsing(data)

        for game in list[0:-1]:
            try:
                dict = crawl_to_dict(game)
            except:
                continue
            df = pd.DataFrame(dict, index=[0])
            df_cleaned = df.dropna(axis=1, how='any')
            if game_info.empty:
                game_info = df
            else:
                try:
                    game_info = pd.concat([game_info, df_cleaned], axis=0, ignore_index=True)
                except:
                    pass
        try:
            next_page_ts = next_timestamp(list[-1])
        except:
            next_page_ts = None

    return game_info