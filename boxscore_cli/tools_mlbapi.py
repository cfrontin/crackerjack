import copy
import json
import os
import urllib.request

from boxscore_cli.tools_linescore import LineScoreInning

_APP_DIR = os.path.split(__file__)[0]  # where this file is installed
_PKG_DIR = os.path.join(_APP_DIR, os.pardir)  # where this package is installed
_MLB_GAME_FORMAT_STRING = "http://statsapi.mlb.com/api/v1.1/game/%s/feed/live?hydrate=officials"  # 6 digit numeric gamepk as string
_MLB_SCHEDULE_FORMAT_STRING = "http://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=%s&endDate=%s"  # dates as string: '2023-01-01'
_MLB_STANDINGS_FORMAT_STRING = "http://statsapi.mlb.com/api/v1/standings?leagueId=%s"  # 3 digit numeric leagueId as string

# things known to the mlbapi
_MLBAM_GAME_LABELS = [
    "Game Scores",
    "WP",
    "Balk",
    "IBB",
    "HBP",
    "Pitches-strikes",
    "Groundouts-flyouts",
    "Batters faced",
    "Inherited runners-scored",
    "Pitch timer violations",
    "Umpires",
    "Weather",
    "Wind",
    "First pitch",
    "T",
    "Att",
    "Venue",
    "Ejections",
]
_MLBAM_TEAM_TYPES = [
    "BATTING",
    "BASERUNNING",
    "FIELDING",
]
_MLBAM_TEAM_BATTING_LABELS = [
    "2b",
    "3b",
    "HR",
    "TB",
    "RB",
    "2-out RBI",
    "Runners left in scoring position, 2 out",
    "SAC",
    "SF",
    "GIDP",
    "Team RISP",
    "Team LOB||",
]
_MLBAM_TEAM_BASERUNNING_LABELS = [
    "SB",
    "CS",
    "PO",
]
_MLBAM_TEAM_FIELDING_LABELS = [
    "E",
    "DP",
    "TP",
    "PB",
    "Outfield assists",
    "Pickoffs",
]
_MLBAM_TEAM_ABBREV = [
    "OAK",
    "PIT",
    "SD",
    "SEA",
    "SF",
    "STL",
    "TB",
    "TEX",
    "TOR",
    "MIN",
    "PHI",
    "ATL",
    "CWS",
    "MIA",
    "NYY",
    "MIL",
    "LAA",
    "AZ",
    "BAL",
    "BOS",
    "CHC",
    "CIN",
    "CLE",
    "COL",
    "DET",
    "HOU",
    "KC",
    "LAD",
    "WSH",
    "NYM",
]

_MLBAM_LEAGUEID_AL = 103
_MLBAM_LEAGUEID_NL = 104
_MLBAM_DIVISIONID_AL_WEST = 200
_MLBAM_DIVISIONID_AL_EAST = 201
_MLBAM_DIVISIONID_AL_CENTRAL = 202
_MLBAM_DIVISIONID_NL_WEST = 203
_MLBAM_DIVISIONID_NL_EAST = 204
_MLBAM_DIVISIONID_NL_CENTRAL = 205


class Team(object):
    """store a team"""

    _location_name: str
    _team_name: str
    _short_name: str
    _abbrev: str
    _is_home: bool

    def __init__(self, location_name_, team_name_, short_name_, abbrev_, is_home_):
        self._location_name = location_name_
        self._team_name = team_name_
        self._short_name = short_name_
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
    def short_name(self):
        """
        the short name on a team, as a string

        e.g. ???
        """
        return self._short_name

    @property
    def abbrev(self):
        """
        the three letter presentation encoding for a team

        e.g. _BAL_ for Baltimore Orioles
        """
        return self._abbrev

    @property
    def full_name(self):
        """
        the full name of a team

        e.g. "Baltimore Orioles" for Baltimore Orioles
        """
        return self.location_name + " " + self.team_name

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


def get_prefixed_player_id(player_id: int):
    return "ID%d" % player_id


def download_json_url(url_str: str, debug_file_loader=None):
    """
    take a URL string, attempt to get the json hosted there, handle response errors
    """

    if debug_file_loader is not None:
        assert os.path.exists(debug_file_loader), (
            "json file at %s must exist." % debug_file_loader
        )
        with open(debug_file_loader, "r") as debug_file:
            data = json.load(debug_file)
        return data

    try:
        with urllib.request.urlopen(url_str) as url:
            data = json.load(url)

        return data
    except urllib.request.HTTPError as e:
        print("\nrequest failed for URL:\n\t" + url_str + "\n")
        print(e)
        return


def translate_gamepk2url(gamepk: int):
    """
    gake a game_pk integer and grab the gameday API link for the game
    """

    gamepk_str = str(gamepk)  # convert game_pk to string
    return _MLB_GAME_FORMAT_STRING % gamepk_str  # drop into format string and return


def download_game_data(gamepk: int, debug=False):
    """
    get the json of data from a given game
    """

    url_str_game = translate_gamepk2url(gamepk)  # get the correct mlbapi url
    debug_filename = os.path.join(_PKG_DIR, "%d.json" % gamepk)
    data_game = download_json_url(
        url_str_game, debug_file_loader=(None if not debug else debug_filename)
    )  # get the json from the link

    return data_game  # return the game data


def extract_venue_name(data_game: dict):
    """
    give a game data dict and get the venue name for printing
    """

    assert "gameData" in data_game
    assert "venue" in data_game["gameData"]
    assert "name" in data_game["gameData"]["venue"]

    return data_game["gameData"]["venue"]["name"]


def extract_decisions(data_game: dict):
    """
    give a game data dict and get the pitching decision
    """

    assert "liveData" in data_game
    data_liveData = data_game["liveData"]

    wp = None
    lp = None
    sv = None

    # if no decisions are posted, dump all Nones
    if "decisions" not in data_liveData:
        return (wp, lp, sv)

    # if they are, hold their data in a useful config
    data_decisions = data_liveData["decisions"]

    # for each key, if it exists, extract player name into var
    # assume last token is last name
    if "winner" in data_decisions:
        wp = data_decisions["winner"]["fullName"].split(" ")[-1]
    if "loser" in data_decisions:
        lp = data_decisions["loser"]["fullName"].split(" ")[-1]
    if "save" in data_decisions:
        sv = data_decisions["save"]["fullName"].split(" ")[-1]

    # dict w/ value if extracted or else None
    decision_dict = {"WP": wp, "LP": lp, "SV": sv}

    return decision_dict


def extract_linescore_data(data_game: dict) -> dict:
    """
    give a game data dict and get the linescore data
    """

    assert "liveData" in data_game
    data_liveData = data_game["liveData"]

    assert "linescore" in data_liveData
    linescore = copy.deepcopy(data_liveData["linescore"])

    return linescore


def extract_teams_data(data_game: dict) -> dict[str:Team]:
    """
    strip and store the basic data for a team for line/boxscore presentation
    """

    assert "gameData" in data_game
    data_gameData = data_game["gameData"]

    assert "teams" in data_gameData
    data_teams = data_gameData["teams"]

    teams = {}
    for key in ("away", "home"):
        assert key in data_teams
        data_team = data_teams[key]
        teamName = data_team["teamName"]
        locationName = data_team["franchiseName"]  # not! data_team["locationName"]
        shortName = data_team["shortName"]
        abbreviation = data_team["abbreviation"]

        teams[key] = Team(
            locationName, teamName, shortName, abbreviation, key == "home"
        )

    return teams


def extract_linescore_innings(data_game: dict):
    """
    get the processed innings data from some game_data
    """

    data_linescore = extract_linescore_data(data_game)  # get the linescore data

    lsi_list = list()

    assert "innings" in data_linescore
    for idx_inn, data_inning in enumerate(data_linescore["innings"]):
        # print("inn. idx.:", idx_inn)
        # print("\tinn. no.:", data_inning["num"], "(%s)" % data_inning["ordinalNum"])
        lsi = LineScoreInning(data_inning["num"])
        lsi.ordinal = data_inning["ordinalNum"]
        lsi.R_away = data_inning["away"].get("runs")
        lsi.H_away = data_inning["away"].get("hits")
        lsi.E_away = data_inning["away"].get("errors")
        lsi.LOB_away = data_inning["away"].get("leftOnBase")
        lsi.R_home = data_inning["home"].get("runs")
        lsi.H_home = data_inning["home"].get("hits")
        lsi.E_home = data_inning["home"].get("errors")
        lsi.LOB_home = data_inning["home"].get("leftOnBase")

        lsi_list.append(lsi)

    return lsi_list


def extract_gamedate(data_game: dict) -> dict:
    """
    give a game data dict and get the date of the game
    """

    assert "liveData" in data_game
    assert "boxscore" in data_game["liveData"]
    assert "info" in data_game["liveData"]["boxscore"]

    info_of_interest = data_game["liveData"]["boxscore"]["info"][-1]
    assert "value" not in info_of_interest

    return info_of_interest["label"]


def extract_player_detailed(data_game: dict, player_id: int) -> dict:
    """
    extract full bio data for a given mlbid
    """

    player_id_prefix = get_prefixed_player_id(player_id)

    assert "gameData" in data_game
    assert "players" in data_game["gameData"]
    assert player_id_prefix in data_game["gameData"]["players"]

    return data_game["gameData"]["players"][player_id_prefix]
