import json
import requests
from data import champion_id

res = requests.get("https://axe.lolalytics.com/tierlist/2/?lane=default&patch=12.22&tier=platinum_plus&queue=420&region=all")

data = json.loads(res.content)['cid']
winrates = {}

for key in data:
    winrate = data[key][3]/data[key][4]
    champ = champion_id[int(key)]
    winrates[champ] = winrate

print(winrates)