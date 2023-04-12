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
    take a URL string, attempt to get the json hosted there
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

    args, arg_filenames = parser.parse_known_args()

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
        print(get_mlbapi_url_gamepk(args.game))
        print()


if __name__ == "__main__":
    main()
