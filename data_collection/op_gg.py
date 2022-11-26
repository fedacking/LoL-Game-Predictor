from datetime import datetime
from http.client import InvalidURL
import traceback
from urllib.error import HTTPError
import urllib.request
import json
from urllib import parse
from data import champion_id, champion_winrate
from threading import Lock

lock = Lock()

opgg_regions = {
    "BR1": "br",
    "LA1": "lan",
    "LA2": "las",
    "NA1": "na",
    "OC1": "oce",
    "EUN1": "eune",
    "EUW1": "euw",
    "RU": "ru",
    "TR1": "tr",
    "JP1": "jp",
    "KR": "kr"
}

def get_summoner_url(name, region):
    region = opgg_regions[region]
    name = parse.quote(name, safe='') 
    return f"https://op.gg/summoners/{region}/{name}/champions"

def get_summoner_api_url(id, region):
    region = opgg_regions[region]
    base_url = "https://op.gg/api/v1.0/internal/bypass/summoners/"
    return base_url + f"{region}/{id}/most-champions/rank?game_type=RANKED&season_id=19"

def get_summoner_id(name, region):
    url = get_summoner_url(name, region)
    res = urllib.request.urlopen(url)
    page = res.read().decode("utf-8")
    start = page.find('"summoner_id":"') + len('"summoner_id":"')
    end = page[start:].find('"')
    return page[start:start+end]

def get_summoner_stats(name, region):
    summoner_id = get_summoner_id(name, region)
    try:
        lock.acquire()
        url = get_summoner_api_url(summoner_id, region)
        lock.release()
        res = urllib.request.urlopen(url)
    except InvalidURL as e:
        print(name, summoner_id, sep=" ")
        raise e
        
    return json.loads(res.read())['data']

def get_player_data(player, champion, region):
    result = {
        "wins": 0,
        "losses": 0,
        "champion_wins": 0,
        "champion_losses": 0,
        "champ_winrate": 0.5,
    }
    stats = get_summoner_stats(player, region)
    try:
        champion_stats = { x["id"]: x for x in stats["champion_stats"]}
        result["wins"] = stats["win"]
        result["losses"] = stats["lose"]
        try:
            result["champion_wins"] = champion_stats[champion]["win"]
            result["champion_losses"] = champion_stats[champion]["lose"]
        except:
            print("Failed to grab champion: " + str(champion) + " for player: " + player)
        champion = champion_id[champion]
        result["champ_winrate"] = champion_winrate[champion]
    except:
        traceback.print_exc()

    return result

if __name__ == "__main__":
    code = 0
    while code != 429:
        try:
            print(datetime.now(), "Running", sep=" ")
            get_summoner_stats("Fedacking", "LA2")
        except HTTPError as e:
            code = e.code
            print(e.headers)