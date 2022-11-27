from datetime import datetime, timedelta
from typing import List
from dotenv import dotenv_values
from pymongo import MongoClient

config = dotenv_values(".env")
uri = "mongodb://" + config["MONGODB_IP"] + ":27017"
client = MongoClient(host=uri)
db = client.lol_predictor
matches = db.matches  # Lista de games en curso que tenemos // V2 de games
entries = db.entries  # Lista de entries para el machine learning
players = db.players  # Lista de players que sabemos que existen


def save_match(game_id, players_in: dict, region):
    if matches.find_one({"game_id": game_id}):
        return False
    matches.insert_one({
        "game_id": game_id,
        "status": 0,  # 0 es insertado en la db,
        # 1 significa que termino
        "region": region,
        "players": players_in,
        "timestamp": datetime.now()
    })
    return True


def get_available_match():
    match = matches.find_one_and_update({
        "status": 0,
        "timestamp": {"$lte": datetime.now() - timedelta(minutes=30)}
    }, {"$set": {"status": 1}})
    if match:
        return match["game_id"], match["players"], match["region"]


def save_entry(game_id, players: List[dict], label):
    if len(players) < 10:
        raise ValueError("Wrong amount of players")

    entry = {
        "game_id": game_id,
        "timestamp": datetime.now(),
        "label": label  # Quien gano, 0 son los jugadores 0-4 y 1 es 5-9
    }

    for i in range(len(players)):
        entry.update({
            f"player_{i}_w": players[i]["wins"],
            f"player_{i}_l": players[i]["losses"],
            f"player_{i}_co_w": players[i]["champion_wins"],
            f"player_{i}_co_l": players[i]["champion_losses"],
            f"player_{i}_ct_wr": players[i]["champ_winrate"],
        })

    entries.insert_one(entry)
    return True


def exists_player(name, region):
    if players.find_one({"name": name, "region": region}):
        return True
    return False


def save_player(name, uuid, region):
    new_player = {
        "name": name,
        "region": region,
        "id": uuid,
        "timestamp": datetime.now(),
        "hits": 1,
        "total": 0
    }
    if players.find_one({"id": uuid}):
        players.find_one_and_replace({"id": uuid}, new_player)
        return False
    if players.find_one({"name": name, "region": region}):
        players.find_one_and_replace({"name": name, "region": region}, new_player)
        return False
    else:
        players.insert_one(new_player)
        return True


def get_available_player():
    many_players = players.find(
        {"timestamp": {"$lte": datetime.now() - timedelta(minutes=30)}},
        options={"limit": 1000}
    )
    player = max(many_players, key=lambda x: x["hits"] / x["total"])
    if player:
        player.update(player, {"timestamp": datetime.now(), "$inc": {"total": 1}})
        return player["id"], player["region"]


def hit_player(player):
    players.find_one_and_update({"id": player["id"], "region": player["region"]}, {"$inc": {"hits": 1}})


def get_entries():
    return list(entries.find({}))
