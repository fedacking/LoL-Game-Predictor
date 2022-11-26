from time import sleep
from dotenv import dotenv_values
from datetime import datetime, timedelta
from requests import HTTPError
from riotwatcher import LolWatcher
import u_gg
import op_gg

WORKERS = 60

config = dotenv_values(".env") 
lol_watcher = LolWatcher(config["RIOT_API_KEY"])

DELAY_SECONDS = 1.2 * WORKERS

regions = [            
    "BR1",
    "LA1",
    "LA2",
    "NA1",
    "OC1",
    "EUN1",
    "EUW1",
    "RU",
    "TR1",
    "JP1",
    "KR"
]

class LoLConnection:
    time: datetime

    def __init__(self) -> None:
        self.time = datetime(1970, 1, 1)

    def _check_time(self):
        if datetime.now() < self.time:
            sleep((self.time - datetime.now()).total_seconds())
            self.time = datetime.now() + timedelta(seconds=DELAY_SECONDS)
        else:
            self.time = datetime.now() + timedelta(seconds=DELAY_SECONDS)

    def featured_games(self, region):
        self._check_time()
        return list(filter(
            lambda x: x["gameMode"] == "CLASSIC" and len(x["bannedChampions"]) > 0,
            lol_watcher.spectator.featured_games(region)['gameList']
        ))

    def player_game(self, region, player_id):
        self._check_time()
        try:
            game = lol_watcher.spectator.by_summoner(region, player_id)
            if game and game["gameMode"] == "CLASSIC" and len(game["bannedChampions"]) > 0:
                return game
        except HTTPError as e:
            if e.response.status_code != 404:
                raise e
        return None

    def match_result(self, game_id, region):
        self._check_time()
        try:
            game_id_sv = region + "_" + str(game_id)
            response = lol_watcher.match.by_id(region, game_id_sv)
            result = {}
            players = response["info"]["participants"]
            for player in players:
                result[player["summonerName"]] = {
                    "id": player["summonerId"],
                    "team_id": player["teamId"],
                    "win": player["win"],
                    "position": player["teamPosition"],
                }
            return result
        except HTTPError as e:
            if e.response.status_code != 404:
                raise e

    def get_player_id(self, player_name, region):
        self._check_time()
        response = lol_watcher.summoner.by_name(region, player_name)
        return response["id"]

    def get_player_data(self, player, champion, region):
            return u_gg.get_player_data(player, champion, region)

