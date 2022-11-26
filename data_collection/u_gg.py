import urllib.request
import json
import requests
from data import champion_winrate, champion_id

def get_u_gg(player, region:str):
    region = region.lower()
    data = {
    "operationName": "getPlayerStats",
    "variables": {
        "summonerName": player,
        "regionId": region,
        "role": 7,
        "seasonId": 18,
        "queueType": [
        420,
        440
        ]
    },
    "query": "query getPlayerStats($queueType: [Int!], $regionId: String!, $role: Int!, $seasonId: Int!, $summonerName: "
            "String!) {\n  fetchPlayerStatistics(\n    queueType: $queueType\n    summonerName: $summonerName\n    "
            "regionId: $regionId\n    role: $role\n    seasonId: $seasonId\n  ) {\n    basicChampionPerformances {\n   "
            "   assists\n      championId\n      cs\n      damage\n      damageTaken\n      deaths\n      "
            "doubleKills\n      gold\n      kills\n      maxDeaths\n      maxKills\n      pentaKills\n      "
            "quadraKills\n      totalMatches\n      tripleKills\n      wins\n      lpAvg\n      __typename\n    }\n    "
            "exodiaUuid\n    puuid\n    queueType\n    regionId\n    role\n    seasonId\n    __typename\n  }\n}\n "
    }
    res = requests.post("https://u.gg/api", json=data)
    if res.status_code != 200:
        raise Exception(f"Status code is not 200, it's {res.status_code}")
    obj = json.loads(res.content)['data']
    return obj


def get_player_data(player, champion, region:str):
    obj = get_u_gg(player, region)
    champs = {}
    for block in obj['fetchPlayerStatistics']:
        for perfomance in block['basicChampionPerformances']:
            champs[perfomance["championId"]] = perfomance
    
    result = {
        "wins": 0,
        "losses": 0,
        "champion_wins": 0,
        "champion_losses": 0,
        "champ_winrate": 0.5,
    }
    
    try:
        result["wins"] = sum(map(lambda x: x["wins"], champs.values()))
        result["losses"] = sum(map(lambda x: x["totalMatches"] - x["wins"], champs.values()))
        result["champion_wins"] = champs[champion]["wins"]
        result["champion_losses"] = champs[champion]["totalMatches"] - champs[champion]["wins"]
    except:
        print("Failed to grab champion: " + str(champion) + " for player: " + player)
    champion = champion_id[champion]
    result["champ_winrate"] = champion_winrate[champion]

    return result