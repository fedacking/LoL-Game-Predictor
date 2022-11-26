from time import sleep
import traceback
from typing import List
from asciimatics.screen import Screen
from datetime import datetime, timedelta
from console import display_status, status, CrawlerStatus
from lol_connection import LoLConnection, WORKERS
from plug_mongo import get_available_player, save_entry, save_match, save_player, get_available_match
from threading import Thread

class EndedGame(Exception):
    pass

def get_player(players, position, team_id):
    return list(filter(
        lambda x: 
            players[x]["position"] == position and
            players[x]["team_id"] == team_id,
        players
    ))[0]


def process_game(conn, game, region):
    game_id = game["gameId"]
    try:
        if conn.match_result(game_id, region):
            raise EndedGame()

        winrates = {}
        players = game["participants"]
        for player in players:
            name = player["summonerName"]
            champ = player["championId"]
            winrates[name] = conn.get_player_data(name, champ, region)

        if conn.match_result(game_id, region):
            raise EndedGame
    except EndedGame:
        return False

    return save_match(game_id, winrates, region)


def process_match(conn:LoLConnection, match):
    match_id = match[0]
    winrates = match[1]
    region = match[2]
    
    future = datetime.now() + timedelta(minutes=60)
    while datetime.now() < future:
        game = conn.match_result(match_id, region)
        if game:
            break
    
    if game:
        for player in game:
            save_player(player, game[player]["id"], region)
        try:
            players_w = [
                get_player(game, "TOP", 100),
                get_player(game, "JUNGLE", 100),
                get_player(game, "MIDDLE", 100),
                get_player(game, "BOTTOM", 100),
                get_player(game, "UTILITY", 100),
                get_player(game, "TOP", 200),
                get_player(game, "JUNGLE", 200),
                get_player(game, "MIDDLE", 200),
                get_player(game, "BOTTOM", 200),
                get_player(game, "UTILITY", 200)
            ]
            label = 0 if game[players_w[0]]["win"] else 1
            players_w = list(map(lambda x: winrates[x], players_w))
            return save_entry(match_id, players_w, label)
        except:
            traceback.print_exc()
    else:
        raise Exception("Game never ends")

def run(status):
    while status.running:
        try:
            match_to_entry(status)
            player_to_match(status)
        except:
            traceback.print_exc()
            status.set_status("Thread crashed")
            sleep(120)
    status.set_status("Thread ended")

def player_to_match(status: CrawlerStatus):
    status.set_status("Searching player")
    conn = LoLConnection()
    player = get_available_player()
    player_num = 0
    while player and status.running:
        (player_id, region) = player
        status.set_status(f"Found Player {player_num}, Searching Game")
        game = conn.player_game(region, player_id)
        if game:
            status.set_status("Found Game")
            if not process_game(conn, game, region):
                status.set_status("Game Ended early")
                player = get_available_player()
            else:
                player = None
        else:
            player = get_available_player()
            player_num += 1

def match_to_entry(status: CrawlerStatus):
    status.set_status("Searching Match")
    conn = LoLConnection()
    match = get_available_match()
    if match:
        status.set_status("Found match, Searching match result")
        process_match(conn, match)
        match = get_available_match()

threads: List[Thread]
threads = []

for i in range(WORKERS):
    status.append(CrawlerStatus(str(i) + " "))
    threads.append(Thread(target=run, args=(status[-1], )))
    threads[-1].start()
    sleep(1)

Screen.wrapper(display_status)

for status in status:
    status.running = False
for thread in threads:
    thread.join()