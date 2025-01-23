import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import importlib
import API
import os
import datetime
from tqdm.notebook import tqdm
import re

def consecutive_game_by(ID, threshold=10, time_th=5):
    reviced_data = [{},{},{}]
    count = 0
    
    path = f'./Data/Subject Crawl/{ID}.csv'
    df = pd.read_csv(path)
    
    df = df[df['win'] != 'draw']    # 다시하기 제외
    df.reset_index(drop=True, inplace=True)
    games = len(df)
        
    box = [[],[],[]]
    for game in range(games):
        timelist = df.loc[game]['playtime'].split(' ')
        minute = float(timelist[0].replace('분', ''))
        second = 0.0
        try:
            second = float(timelist[1].replace('초', ''))
        except:
            pass
        time = float(minute) + float(second) / 60
        gpm = df.loc[game]['gold']/time
        # 첫번째는 무조건 넣기
        if game == 0:
            box[0].append(df.loc[game]['win'])
            box[1].append(df.loc[game]['cs_per_minute'])
            box[2].append(gpm)
            
        # 시간 간격이 time_th보다 길면 box를 초기화하고 첫번째 넣기
        else:
            if (df.loc[game-1]['start'] - df.loc[game]['end'])/60 > time_th:
                box = [[],[],[]]
            box[0].append(df.loc[game]['win'])
            box[1].append(df.loc[game]['cs_per_minute'])
            box[2].append(gpm)

        # box의 길이가 threshold가 되면 dict에 저장
        if len(box[0]) == threshold:
            reviced_data[0][count] = box[0][:threshold]
            reviced_data[1][count] = box[1][:threshold]
            reviced_data[2][count] = box[2][:threshold]
            
            count += 1

    result_win = pd.DataFrame(reviced_data[0])
    result_cs = pd.DataFrame(reviced_data[1])
    result_gold = pd.DataFrame(reviced_data[2])

    print(f'ID {ID}: number of data = {len(result_win.columns)}')

    # 저장
    result_win.to_csv(f'./Data/Subject Data/{ID}_consecutive_win_count{threshold}_term{time_th}.csv')
    result_cs.to_csv(f'./Data/Subject Data/{ID}_consecutive_cs_count{threshold}_term{time_th}.csv')
    result_gold.to_csv(f'./Data/Subject Data/{ID}_consecutive_gold_count{threshold}_term{time_th}.csv')

    return len(result_win.columns)

def draw_winrate(ID, count, term):
    winloss = pd.read_csv(f'./Data/Subject Data/{ID}_consecutive_win_count{count}_term{term}.csv').T

    winloss.drop('Unnamed: 0')
    pd.set_option('future.no_silent_downcasting', True)
    winloss.replace({'win': 1, 'loss': 0}, inplace=True)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    x = [i for i in range(1, count+1)]

    ax.plot(x, winloss.mean())

    ax.set_xticks(x)
    ax.set_title(f'ID {ID}: number of data = {len(winloss)}')

    plt.savefig(f'./Data/Image/{ID}_plot_win_count{count}_term{term}.png')

    plt.close()

def draw_cpm(ID, count, term):
    cpm = pd.read_csv(f'./Data/Subject Data/{ID}_consecutive_cs_count{count}_term{term}.csv').T
    cpm.drop('Unnamed: 0')

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    x = [i for i in range(1, count+1)]
    ax.plot(x, cpm.mean())

    ax.set_xticks(x)
    ax.set_title(f'ID {ID}: number of data = {len(cpm)}')

    plt.savefig(f'./Data/Image/{ID}_plot_cs_count{count}_term{term}.png')

    plt.close()

def draw_gpm(ID, count, term):
    gold = pd.read_csv(f'./Data/Subject Data/{ID}_consecutive_gold_count{count}_term{term}.csv').T
    gold.drop('Unnamed: 0')

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    x = [i for i in range(1, count+1)]
    ax.plot(x, gold.mean())

    ax.set_xticks(x)
    ax.set_title(f'ID {ID}: number of data = {len(gold)}')

    plt.savefig(f'./Data/Image/{ID}_plot_gold_count{count}_term{term}.png')

    plt.close()