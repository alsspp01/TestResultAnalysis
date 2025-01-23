import requests as rq
import json
import re
import csv
import time

REQ_TERM = 1.25  # API requset limit

# tier, division 목록
high_tier = ['CHALLENGER', 'GRANDMASTER', 'MASTER']
low_tier = ['DIAMOND', 'EMERALD', 'PLATINUM', 'GOLD', 'SILVER', 'BRONZE']
tiers = ['CHALLENGER', 'GRANDMASTER', 'MASTER', 'DIAMOND', 'EMERALD', 'PLATINUM', 'GOLD', 'SILVER', 'BRONZE']
tiers_tft = tiers[3:]
division = ['I', 'II', 'III', 'IV']


def summonerData(tier, division, page, api_key):
    url = f"https://kr.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/{tier}/{division}?page={page}"
    header = {"X-Riot-Token": api_key}
    data = rq.get(url, headers=header).json()
    result = []
    for temp in data:
        result.append(temp['summonerId'])

    time.sleep(REQ_TERM)

    return result

def summonerTopuuid(summonerId, api_key):
    url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/{summonerId}"
    header = {"X-Riot-Token": api_key}

    time.sleep(REQ_TERM)

    return rq.get(url, headers=header).json()['puuid']

def puuidTogameName(puuid, api_key):
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
    header = {"X-Riot-Token": api_key}

    time.sleep(REQ_TERM)

    return rq.get(url, headers=header).json()
    
def puuidTomatchId(puuid, api_key, count=100):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count={count}"
    header = {"X-Riot-Token": api_key}

    time.sleep(REQ_TERM)

    return rq.get(url, headers=header).json()
    
def gameInfo(matchId, api_key):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{matchId}"
    header = {"X-Riot-Token": api_key}

    time.sleep(REQ_TERM)

    return rq.get(url, headers=header).json()

def timeline(matchId, api_key):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{matchId}/timeline"
    header = {"X-Riot-Token": api_key}

    time.sleep(REQ_TERM)

    return rq.get(url, headers=header).json()

def tft_summonerData(tier, division, page, api_key):
    url = f"https://kr.api.riotgames.com/tft/league/v1/entries/{tier}/{division}?queue=RANKED_TFT&page={page}"
    header = {"X-Riot-Token": api_key}
    response = rq.get(url, headers=header)
    result = []

    if response.status_code == 200:
        data = response.json()

        for temp in data:
            result.append(temp['puuid'])

    time.sleep(REQ_TERM)

    return result

def tft_puuidTomatchId(puuid, api_key):
    url = f"https://asia.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids"
    header = {"X-Riot-Token": api_key}

    time.sleep(REQ_TERM)

    return rq.get(url, headers=header).json()

def tft_gameInfo(matchId, api_key):
    url = f"https://asia.api.riotgames.com/tft/match/v1/matches/{matchId}"
    header = {"X-Riot-Token": api_key}

    time.sleep(REQ_TERM)

    return rq.get(url, headers=header).json()

def gameNameTopuuid(gameName, tagLine, api_key):
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
    header = {"X-Riot-Token": api_key}

    time.sleep(REQ_TERM)

    return rq.get(url, headers=header).json()