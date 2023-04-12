#!/usr/bin/env python3

import os.path
import argparse
import json
import copy

import urllib.request
import pprint as pp

# some private global variables
_APP_DIR = os.path.split(__file__)[0]  # where this file is installed
_MLB_GAME_FORMAT_STRING = "https://statsapi.mlb.com/api/v1.1/game/%s/feed/live?hydrate=officials"  # 6 digit numeric gamepk as string
_MLB_SCHEDULE_FORMAT_STRING = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=%s&endDate=%s"  # dates as string: '2023-01-01'


class Team(object):
    """store a team"""

    _location_name: str
    _team_name: str
    _abbrev: str
    _is_home: bool

    def __init__(self, location_name_, team_name_, abbrev_, is_home_):
        self._location_name = location_name_
        self._team_name = team_name_
        self._abbrev = abbrev_
        self._is_home = is_home_

    @property
    def location_name(self):
        """
        the location name on a team, as a string

        e.g. _Baltimore_ in _Baltimore_ Orioles
        """
        return self._location_name

    @property
    def team_name(self):
        """
        the team name on a team, as a string

        e.g. _Orioles_ in Baltimore _Orioles_
        """
        return self._team_name

    @property
    def abbrev(self):
        """
        the three letter presentation encoding for a team

        e.g. _BAL_ for Baltimore Orioles
        """
        return self._abbrev

    @property
    def is_home(self):
        """flag for if the team is the home team in a given context"""
        return self._is_home

    def __str__(self):
        return "%s (%s): %s %s" % (
            self.abbrev,
            "home" if self.is_home else "away",
            self.location_name,
            self.team_name,
        )


class LineScoreInning(object):
    """
    store a linescore inning
    """

    _inn_no: int
    _R_away: int
    _H_away: int
    _E_away: int
    _LOB_away: int
    _R_home: int
    _H_home: int
    _E_home: int
    _LOB_home: int
    _ordinal: str

    @property
    def inn_no(self):
        return self._inn_no

    @inn_no.setter
    def inn_no(self, value):
        self._inn_no = value

    @property
    def ordinal(self):
        return self._ordinal

    @ordinal.setter
    def ordinal(self, value):
        self._ordinal = value

    @property
    def R_away(self):
        return self._R_away

    @R_away.setter
    def R_away(self, value):
        self._R_away = value

    @property
    def H_away(self):
        return self._H_away

    @H_away.setter
    def H_away(self, value):
        self._H_away = value

    @property
    def E_away(self):
        return self._E_away

    @E_away.setter
    def E_away(self, value):
        self._E_away = value

    @property
    def LOB_away(self):
        return self._LOB_away

    @LOB_away.setter
    def LOB_away(self, value):
        self._LOB_away = value

    @property
    def R_home(self):
        return self._R_home

    @R_home.setter
    def R_home(self, value):
        self._R_home = value

    @property
    def H_home(self):
        return self._H_home

    @H_home.setter
    def H_home(self, value):
        self._H_home = value

    @property
    def E_home(self):
        return self._E_home

    @E_home.setter
    def E_home(self, value):
        self._E_home = value

    @property
    def LOB_home(self):
        return self._LOB_home

    @LOB_home.setter
    def LOB_home(self, value):
        self._LOB_home = value

    def __init__(self, inn_no: int, away=[0, 0, 0, 0], home=[0, 0, 0, 0]):
        """
        create an inning object
        """

        self._inn_no = inn_no
        self.R_away = away[0]
        self.H_away = away[1]
        self.E_away = away[2]
        self.LOB_away = away[3] if len(away) > 3 else None
        self.R_home = home[0]
        self.H_home = home[1]
        self.E_home = home[2]
        self.LOB_home = home[3] if len(home) > 3 else None


def print_dummy_linescore():
    """
    print a dummy linescore for demo purposes
    """

    filename_linescore = os.path.join(_APP_DIR, "linescore_dummy.txt")
    with open(filename_linescore, "r") as f:
        linescore_str = f.read()

    print()
    print(linescore_str)
    print()


def print_dummy_boxscore():
    """
    print a dummy boxscore for demo purposes
    """

    filename_boxscore = os.path.join(_APP_DIR, "boxscore_dummy.txt")
    with open(filename_boxscore, "r") as f:
        boxscore_str = f.read()

    print()
    print(boxscore_str)
    print()


def url_to_json(url_str: str):
    """
    take a URL string, attempt to get the json hosted there, handle response errors
    """

    try:
        with urllib.request.urlopen(url_str) as url:
            data = json.load(url)

        return data
    except urllib.request.HTTPError as e:
        print("\nrequest failed for URL:\n\t" + url_str + "\n")
        print(e)
        return


def get_mlbapi_url_gamepk(gamepk: int):
    """
    gake a game_pk integer and grab the gameday API link for the game
    """

    gamepk_str = str(gamepk)  # convert game_pk to string
    return _MLB_GAME_FORMAT_STRING % gamepk_str  # drop into format string and return


def get_game_data(gamepk: int):
    """
    get the json of data from a given game
    """

    url_str_game = get_mlbapi_url_gamepk(gamepk)  # get the correct mlbapi url
    data_game = url_to_json(url_str_game)  # get the json from the link

    return data_game  # return the game data


def strip_linescore_data(data_game: dict):
    """
    give a game_pk and get the linescore data
    """

    assert "liveData" in data_game
    data_liveData = data_game["liveData"]

    assert "linescore" in data_liveData
    linescore = copy.deepcopy(data_liveData["linescore"])

    return linescore


def strip_boxscore_data(data_game: dict):
    """
    give a game_pk and get the boxscore data
    """

    assert "liveData" in data_game
    data_liveData = data_game["liveData"]

    assert "boxscore" in data_liveData
    boxscore = copy.deepcopy(data_liveData["boxscore"])

    return boxscore


def strip_teams_data(data_game: dict):
    """strip and store the basic data for a team for line/boxscore presentation"""

    assert "gameData" in data_game
    data_gameData = data_game["gameData"]

    assert "teams" in data_gameData
    data_teams = data_gameData["teams"]

    teams = {}
    for key in ("away", "home"):
        assert key in data_teams
        data_team = data_teams[key]
        teamName = data_team["teamName"]
        locationName = data_team["locationName"]
        abbreviation = data_team["abbreviation"]

        teams[key] = Team(locationName, teamName, abbreviation, key == "home")

    return teams


def strip_linescore_innings(data_game: dict):
    data_linescore = strip_linescore_data(data_game)  # get the linescore data

    lsi_list = list()

    assert "innings" in data_linescore
    for idx_inn, data_inning in enumerate(data_linescore["innings"]):
        print("inn. idx.:", idx_inn)
        print("\tinn. no.:", data_inning["num"], "(%s)" % data_inning["ordinalNum"])
        lsi = LineScoreInning(data_inning["num"])
        lsi.ordinal = data_inning["ordinalNum"]
        lsi.R_away = data_inning["away"]["runs"]
        lsi.H_away = data_inning["away"]["hits"]
        lsi.E_away = data_inning["away"]["errors"]
        lsi.LOB_away = data_inning["away"]["leftOnBase"]
        lsi.R_home = (
            data_inning["home"]["runs"] if "runs" in data_inning["home"] else None
        )
        lsi.H_home = (
            data_inning["home"]["hits"] if "hits" in data_inning["home"] else None
        )
        lsi.E_home = (
            data_inning["home"]["errors"] if "errors" in data_inning["home"] else None
        )
        lsi.LOB_home = (
            data_inning["home"]["leftOnBase"]
            if "leftOnBase" in data_inning["home"]
            else None
        )

        lsi_list.append(lsi)

    return lsi_list


def main():
    ### parse CLI arguments

    parser = argparse.ArgumentParser(
        prog="boxscore",
        description="cfrontin's CLI boxscore and linescore printer",
        epilog="strike three!\a\n",
    )
    parser.add_argument("-l", "--line", action="store_true", default=False)
    parser.add_argument("-b", "--box", action="store_true", default=False)
    parser.add_argument("-g", "--game", action="store", default=None, type=int)

    args = parser.parse_args()

    ### do functionality

    if args.line:
        print_dummy_linescore()

    if args.box:
        print_dummy_boxscore()

    if args.game:  # exploration mode
        game_data = get_game_data(args.game)
        print()
        pp.pprint(game_data, compact=True, indent=1, depth=2)
        print()
        pp.pprint(strip_linescore_data(game_data), compact=True, indent=1, depth=2)
        # print()
        # pp.pprint(strip_boxscore_data(game_data), compact=True, indent=1, depth=2)
        print()
        print(strip_teams_data(game_data)["away"])
        print(strip_teams_data(game_data)["home"])
        print()
        print(strip_linescore_innings(game_data))
        print()
        print(get_mlbapi_url_gamepk(args.game))
        print()


if __name__ == "__main__":
    main()
