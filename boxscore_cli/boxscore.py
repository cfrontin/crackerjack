#!/usr/bin/env python3

import os
import os.path
import argparse
import json
import copy
from collections import OrderedDict

import urllib.request
import pprint as pp

# some private global variables
_APP_DIR = os.path.split(__file__)[0]  # where this file is installed
_PKG_DIR = os.path.join(_APP_DIR, os.pardir)  # where this package is installed
_MLB_GAME_FORMAT_STRING = "https://statsapi.mlb.com/api/v1.1/game/%s/feed/live?hydrate=officials"  # 6 digit numeric gamepk as string
_MLB_SCHEDULE_FORMAT_STRING = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=%s&endDate=%s"  # dates as string: '2023-01-01'
_CLI_LINE_LENGTH_DEFAULT = 80

# labels known to the mlbapi
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

    def get_appetite(self) -> int:
        """
        figure out how many characters this inning needs to print
        """

        vars = [
            self._inn_no,
            self._R_away,
            self._H_away,
            self._E_away,
            self._LOB_away,
            self._R_home,
            self._H_home,
            self._E_home,
            self._LOB_home,
        ]

        # return the longest length of the converted string
        return max([len(str(var)) for var in vars if var is not None])


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
        url_str_game, debug_file_loader=None if not debug else debug_filename
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
        locationName = data_team["locationName"]
        abbreviation = data_team["abbreviation"]

        teams[key] = Team(locationName, teamName, abbreviation, key == "home")

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


def extract_RHE(linescoreinning_list: list[LineScoreInning]):
    R_away = 0
    R_home = 0
    H_away = 0
    H_home = 0
    E_away = 0
    E_home = 0
    LOB_away = 0
    LOB_home = 0

    for lsi in linescoreinning_list:
        R_away += lsi.R_away if lsi.R_away is not None else 0
        R_home += lsi.R_home if lsi.R_home is not None else 0
        H_away += lsi.H_away if lsi.H_away is not None else 0
        H_home += lsi.H_home if lsi.H_home is not None else 0
        E_away += lsi.E_away if lsi.E_away is not None else 0
        E_home += lsi.E_home if lsi.E_home is not None else 0
        LOB_away += lsi.LOB_away if lsi.LOB_away is not None else 0
        LOB_home += lsi.LOB_home if lsi.LOB_home is not None else 0

    RHE_dict = {}
    RHE_dict["R"] = {
        "spaces": max([len(str(x)) for x in [R_away, R_home]]),
        "away": R_away,
        "home": R_home,
    }
    RHE_dict["H"] = {
        "spaces": max([len(str(x)) for x in [H_away, H_home]]),
        "away": H_away,
        "home": H_home,
    }
    RHE_dict["E"] = {
        "spaces": max([len(str(x)) for x in [E_away, E_home]]),
        "away": E_away,
        "home": E_home,
    }
    RHE_dict["LOB"] = {
        "spaces": max([len(str(x)) for x in [LOB_away, LOB_home]]),
        "away": LOB_away,
        "home": LOB_home,
    }

    return RHE_dict


def format_linescore(
    linescoreinning_list: list[LineScoreInning],
    teams: dict[Team],
    decision_dict=None,
    venue=None,
    cross_char="+",
    vert_char="|",
    horz_char="-",
    min_spaces_dense=2,
    min_spaces_sparse=1,
    indent_dense=0,
    indent_sparse=2,
    force_uppercase_team=True,
    use_top_spacing_line=False,
    use_bottom_spacing_line=False,
) -> list[str]:
    """
    TODO: create this documentation
    """

    # craete the format string
    format_name_dense = ""
    format_name_sparse = ""
    format_line_dense = ""
    format_line_sparse = ""

    # create substitution sets for each line permutation
    substitution_set_name_top_dense = []
    substitution_set_name_away_dense = []
    substitution_set_name_home_dense = []
    substitution_set_name_bot_dense = []
    substitution_set_name_top_sparse = []
    substitution_set_name_away_sparse = []
    substitution_set_name_home_sparse = []
    substitution_set_line_top_dense = []
    substitution_set_line_away_dense = []
    substitution_set_line_home_dense = []
    substitution_set_line_bot_dense = []
    substitution_set_line_top_sparse = []
    substitution_set_line_away_sparse = []
    substitution_set_line_home_sparse = []

    # start a count of the spaces
    spaces_linescore_dense = 0
    spaces_linescore_sparse = 0

    # add the indentation
    spaces_linescore_dense += indent_dense
    format_name_dense += " " * indent_dense
    spaces_linescore_sparse += indent_sparse
    format_name_sparse += " " * indent_sparse

    # add the stuff before the innings
    spaces_linescore_dense += 2  # border char and one space before name
    format_name_dense += "%1s "
    substitution_set_name_top_dense.append(cross_char)
    substitution_set_name_away_dense.append(vert_char)
    substitution_set_name_home_dense.append(vert_char)
    substitution_set_name_bot_dense.append(cross_char)
    spaces_linescore_dense += 3  # border char and one space (at least) after name
    format_line_dense += " %1s "
    substitution_set_line_top_dense.append(cross_char)
    substitution_set_line_away_dense.append(cross_char)
    substitution_set_line_home_dense.append(cross_char)
    substitution_set_line_bot_dense.append(cross_char)
    spaces_linescore_sparse += 2  # border char and one space before name
    format_name_sparse += ""
    spaces_linescore_sparse += 1  # border char and one space (at least) after name
    format_line_sparse += " "

    # loop through the innings, formatting on the fly
    for idx_lsi, lsi in enumerate(linescoreinning_list):
        # spaces_linescore_dense += 1 # border char before
        spaces_linescore_dense += 1  # buffer space before
        spaces_linescore_dense += max(
            lsi.get_appetite(), min_spaces_dense
        )  # spaces needed for this lsi element
        spaces_linescore_dense += 1  # buffer space after
        spaces_linescore_dense += 1  # border char after
        format_line_dense += (
            " %" + str(max(lsi.get_appetite(), min_spaces_dense)) + "s %1s"
        )
        substitution_set_line_top_dense.append(lsi.inn_no)
        substitution_set_line_away_dense.append(lsi.R_away)
        substitution_set_line_home_dense.append(
            lsi.R_home if lsi.R_home is not None else " " * lsi.get_appetite()
        )
        substitution_set_line_bot_dense.append(horz_char * lsi.get_appetite())
        substitution_set_line_top_dense.append(cross_char)
        substitution_set_line_away_dense.append(cross_char)
        substitution_set_line_home_dense.append(cross_char)
        substitution_set_line_bot_dense.append(cross_char)

        if (idx_lsi % 3 == 0) and (idx_lsi != 0):
            spaces_linescore_sparse += 2  # every three innings, add extra spaces before
            format_line_sparse += "  "
        spaces_linescore_sparse += max(
            lsi.get_appetite(), min_spaces_sparse
        )  # space needed for this lsi element
        spaces_linescore_sparse += 1  # buffer space after
        format_line_sparse += (
            "%" + str(max(lsi.get_appetite(), min_spaces_sparse)) + "s "
        )
        substitution_set_line_top_sparse.append(lsi.inn_no)
        substitution_set_line_away_sparse.append(lsi.R_away)
        substitution_set_line_home_sparse.append(
            lsi.R_home if lsi.R_home is not None else " " * lsi.get_appetite()
        )

    # work on RHE ending
    spaces_linescore_sparse += 2  # buffer spaces before summary
    format_line_sparse += " -"
    RHE_dict = extract_RHE(linescoreinning_list)  # get the RHE stuff
    for RHEcode in ["R", "H", "E"]:
        spaces_linescore_dense += 1  # buffer space before summary term
        spaces_linescore_dense += RHE_dict[RHEcode]["spaces"]
        spaces_linescore_dense += 1  # buffer space after summary term
        spaces_linescore_dense += 1  # border char after summary term
        format_line_dense += " %" + str(RHE_dict[RHEcode]["spaces"]) + "s %1s"
        substitution_set_line_top_dense.append(RHEcode)
        substitution_set_line_away_dense.append(RHE_dict[RHEcode]["away"])
        substitution_set_line_home_dense.append(RHE_dict[RHEcode]["home"])
        substitution_set_line_bot_dense.append(horz_char * RHE_dict[RHEcode]["spaces"])
        substitution_set_line_top_dense.append(cross_char)
        substitution_set_line_away_dense.append(cross_char)
        substitution_set_line_home_dense.append(cross_char)
        substitution_set_line_bot_dense.append(cross_char)

        spaces_linescore_sparse += 1  # buffer spaces before summary term
        spaces_linescore_sparse += RHE_dict[RHEcode]["spaces"]
        format_line_sparse += " %" + str(RHE_dict[RHEcode]["spaces"]) + "s"
        substitution_set_line_top_sparse.append(RHEcode)
        substitution_set_line_away_sparse.append(RHE_dict[RHEcode]["away"])
        substitution_set_line_home_sparse.append(RHE_dict[RHEcode]["home"])

    residual_spaces_dense = _CLI_LINE_LENGTH_DEFAULT - spaces_linescore_dense
    residual_spaces_sparse = _CLI_LINE_LENGTH_DEFAULT - spaces_linescore_sparse

    spaces_team_fullname = max([len(team.full_name) for team in teams.values()])
    spaces_team_cityname = max([len(team.location_name) for team in teams.values()])

    def dtf(x_in):
        if force_uppercase_team:
            return x_in.upper()
        return x_in  # pass through

    if residual_spaces_dense > spaces_team_fullname:
        format_name_dense += (
            "%" + str(residual_spaces_dense) + "s"
        )  # fill remaining spaces
        substitution_set_name_top_dense.append(horz_char * residual_spaces_dense)
        substitution_set_name_away_dense.append(dtf(teams["away"].full_name))
        substitution_set_name_home_dense.append(dtf(teams["home"].full_name))
        substitution_set_name_bot_dense.append(horz_char * residual_spaces_dense)
    elif residual_spaces_dense > spaces_team_cityname:
        format_name_dense += (
            "%-" + str(residual_spaces_dense) + "s"
        )  # fill remaining spaces
        substitution_set_name_top_dense.append(horz_char * residual_spaces_dense)
        substitution_set_name_away_dense.append(dtf(teams["away"].location_name))
        substitution_set_name_home_dense.append(dtf(teams["home"].location_name))
        substitution_set_name_bot_dense.append(horz_char * residual_spaces_dense)
    else:
        magic_number = max(3, residual_spaces_dense)
        format_name_dense += "%" + str(magic_number) + "s"
        substitution_set_name_top_dense.append(horz_char * magic_number)
        substitution_set_name_away_dense.append(teams["away"].abbrev)
        substitution_set_name_home_dense.append(teams["home"].abbrev)
        substitution_set_name_bot_dense.append(horz_char * magic_number)
    format_name_sparse += "%3s  "
    substitution_set_name_top_sparse.append(horz_char * 3)
    substitution_set_name_away_sparse.append(teams["away"].abbrev)
    substitution_set_name_home_sparse.append(teams["home"].abbrev)

    lines_dense = []
    lines_sparse = []

    # print the results (DEBUG!!!!!)
    lines_dense.append(
        (format_name_dense % tuple(substitution_set_name_top_dense))
        + (format_line_dense % tuple(substitution_set_line_top_dense))
    )
    if use_top_spacing_line:
        lines_dense.append(
            (format_name_dense % tuple(substitution_set_name_bot_dense))
            + (format_line_dense % tuple(substitution_set_line_bot_dense))
        )
    lines_dense.append(
        (format_name_dense % tuple(substitution_set_name_away_dense))
        + (format_line_dense % tuple(substitution_set_line_away_dense))
    )
    lines_dense.append(
        (format_name_dense % tuple(substitution_set_name_home_dense))
        + (format_line_dense % tuple(substitution_set_line_home_dense))
    )
    if use_bottom_spacing_line:
        lines_dense.append(
            (format_name_dense % tuple(substitution_set_name_bot_dense))
            + (format_line_dense % tuple(substitution_set_line_bot_dense))
        )

    lines_sparse.append(
        (format_name_sparse % tuple(substitution_set_name_away_sparse))
        + (format_line_sparse % tuple(substitution_set_line_away_sparse))
    )
    lines_sparse.append(
        (format_name_sparse % tuple(substitution_set_name_home_sparse))
        + (format_line_sparse % tuple(substitution_set_line_home_sparse))
    )

    if venue is not None:
        venue_line = " " * indent_dense
        venue_line += cross_char + " "
        venue = " " + venue + " "  # add leading and trailing space
        venue_line_ending = cross_char + horz_char * 3 + cross_char
        fill_horz_char_venue = (
            _CLI_LINE_LENGTH_DEFAULT
            - len(venue_line)
            - len(venue)
            - len(venue_line_ending)
            - 1
        )
        venue_line += (
            horz_char * fill_horz_char_venue
            + cross_char
            + dtf(venue)
            + venue_line_ending
        )
        lines_dense.append(venue_line)

    if decision_dict is not None:
        decision_line = " " * indent_dense
        decision_line += cross_char + horz_char * 3 + cross_char
        spacer = cross_char + horz_char + cross_char
        dec_list = []
        for key in ["WP", "LP", "SV"]:
            if decision_dict[key] is not None:
                dec_list.append("%s: " % key + decision_dict[key])
        for idx_dec, dec_val in enumerate(dec_list):
            decision_line += " " + dtf(dec_val) + " "
            if idx_dec + 1 < len(dec_list):
                decision_line += spacer
            else:
                decision_line += cross_char
        fill_horz_char_decision = _CLI_LINE_LENGTH_DEFAULT - len(decision_line) - 1
        decision_line += horz_char * fill_horz_char_decision + cross_char
        lines_dense.append(decision_line)

    return lines_dense, lines_sparse


def extract_boxscore_data(data_game: dict) -> dict:
    """
    give a game_pk and get the boxscore data
    """

    assert "liveData" in data_game
    data_liveData = data_game["liveData"]

    assert "boxscore" in data_liveData
    boxscore = copy.deepcopy(data_liveData["boxscore"])

    return boxscore


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


def extract_info_box(
    data_game: dict,
    labels_to_skip: list = [
        "Venue",
    ],
) -> OrderedDict[str:list]:
    """
    extract the bottom-line box score info

    info is stored as a list of info types, with a possibly-singleton list
    """

    assert "liveData" in data_game
    assert "boxscore" in data_game["liveData"]
    assert "info" in data_game["liveData"]["boxscore"]

    lines = OrderedDict()
    info_field_list = copy.deepcopy(
        data_game["liveData"]["boxscore"]["info"][:-1]
    )  # scrape off date, copy for mods
    for info_field in info_field_list:
        assert info_field["label"] in _MLBAM_GAME_LABELS, (
            "%s must be in game labels" % info_field["label"]
        )
        if info_field["label"] in labels_to_skip:
            continue  # skip stuff that should be skipped
        if info_field["value"].endswith("."):
            info_field["value"] = info_field["value"][:-1]  # trim trailing period
        info_field["value"] = [x.strip() for x in info_field["value"].split(";")]
        # print("%s:" % info_field["label"])
        # [print("\t%s" % x) for x in info_field["value"]]
        lines[info_field["label"]] = info_field["value"]

    return lines


def extract_info_team(
    data_game: dict,
    home_team: bool,
    labels_to_skip: list = [],
) -> dict[OrderedDict[str:list]]:
    """
    extract the bottom-lines team box score info
    """

    team_key = "home" if home_team else "away"

    assert "liveData" in data_game
    assert "boxscore" in data_game["liveData"]
    assert "teams" in data_game["liveData"]["boxscore"]
    assert team_key in data_game["liveData"]["boxscore"]["teams"]

    team_data = copy.deepcopy(data_game["liveData"]["boxscore"]["teams"][team_key])
    assert "info" in team_data

    lines = {}

    for title_sec in team_data["info"]:
        info_title = title_sec["title"]
        dict_entry = OrderedDict()
        assert info_title in _MLBAM_TEAM_TYPES
        for info_field in title_sec["fieldList"]:
            if info_field in labels_to_skip:
                continue  # skip stuff that should be skipped
            if info_field["value"].endswith("."):
                info_field["value"] = info_field["value"][:-1]  # trim trailing period
            info_field["value"] = [x.strip() for x in info_field["value"].split(";")]
            # print(info_field["label"])
            # [print("\t%s" % x) for x in info_field["value"]]
            dict_entry[info_field["label"]] = info_field["value"]
        lines[info_title] = dict_entry

    return lines


def format_info_box(
    info_box: OrderedDict[str:list], indent_size=2, init_indent=1
) -> list[str]:
    """
    get lines to print box info

    take the box score info, and make lines to display nicely without overrunning,
    given some indentation specifications
    """

    lines = []

    for key, values in info_box.items():
        working_str = " " * indent_size * init_indent + key + ": "
        for idx_value, value in enumerate(values):
            if (
                len(working_str)
                + len(value)
                + (2 if (idx_value + 1 != len(values)) else 0)
                > _CLI_LINE_LENGTH_DEFAULT
            ):
                lines.append(working_str)
                working_str = (
                    " " * indent_size * (init_indent + 2)
                    + value
                    + ("; " if (idx_value + 1 != len(values)) else "")
                )
            else:
                working_str += value + ("; " if (idx_value + 1 != len(values)) else "")
        lines.append(working_str)

    return lines


def format_info_team(
    info_team: dict[OrderedDict[str:list]],
    indent_size=2,
    init_indent=2,
):
    """
    get lines to print team info

    take the team score info, make lines to display nicely without overrunning,
    given some indentation specifications
    """

    lines = []

    for team_type in _MLBAM_TEAM_TYPES:
        if team_type in info_team:
            lines.append(" " * indent_size * init_indent + team_type)

            next_indent = init_indent + 1

            for key, values in info_team[team_type].items():
                working_str = " " * indent_size * next_indent + key + ": "
                for idx_value, value in enumerate(values):
                    if (
                        len(working_str)
                        + len(value)
                        + (2 if (idx_value + 1 != len(values)) else 0)
                        > _CLI_LINE_LENGTH_DEFAULT
                    ):
                        lines.append(working_str)
                        working_str = (
                            " " * indent_size * (next_indent + 2)
                            + value
                            + ("; " if (idx_value + 1 != len(values)) else "")
                        )
                    else:
                        working_str += value + (
                            "; " if (idx_value + 1 != len(values)) else ""
                        )
                lines.append(working_str)

    return lines


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
    parser.add_argument("--debug", action="store_true", default=False)

    args = parser.parse_args()

    ### do functionality

    if args.line:
        game_data = download_game_data(args.game, debug=args.debug)
        dense_lines, _ = format_linescore(
            extract_linescore_innings(game_data),
            extract_teams_data(game_data),
            venue=extract_venue_name(game_data),
            decision_dict=extract_decisions(game_data),
        )
        print()
        [print(line) for line in dense_lines]
        print()
        # # OLD DUMMY VERSION
        # print_dummy_linescore()

    if args.box:
        print_dummy_boxscore()

    if args.game and (not args.line):  # exploration mode
        game_data = download_game_data(args.game, debug=True)
        print()
        pp.pprint(game_data, compact=True, indent=1, depth=2)
        # print()
        # pp.pprint(extract_linescore_data(game_data), compact=True, indent=1, depth=2)
        # print()
        # print(extract_teams_data(game_data)["away"])
        # print(extract_teams_data(game_data)["home"])
        # print()
        # print(extract_linescore_innings(game_data))
        # print()
        # print([x.get_appetite() for x in extract_linescore_innings(game_data)])
        # print()
        # lines_dense, lines_sparse = format_linescore(
        #     extract_linescore_innings(game_data),
        #     extract_teams_data(game_data),
        #     venue=extract_venue_name(game_data),
        #     decision_dict=extract_decisions(game_data),
        # )
        # print("dense linescore:\n")
        # [print(x) for x in lines_dense]
        # print()
        # print("sparse linescore:\n")
        # [print(x) for x in lines_sparse]
        # print()
        # print(translate_gamepk2url(args.game))
        # print()
        # print(extract_decisions(game_data))
        # print()
        print()
        pp.pprint(extract_boxscore_data(game_data), compact=True, indent=1, depth=2)
        print("\n")
        print(extract_gamedate(game_data))
        print(extract_venue_name(game_data))
        print()
        lines_dense, lines_sparse = format_linescore(
            extract_linescore_innings(game_data),
            extract_teams_data(game_data),
            use_top_spacing_line=False,
            use_bottom_spacing_line=False,
            horz_char=" ",
            vert_char=" ",
            cross_char=" ",
        )
        do_dense = True
        if do_dense:
            [print(line) for line in lines_dense]
        else:
            [print(line) for line in lines_sparse]
        print()
        print("  ", extract_teams_data(game_data)["away"], sep="")
        print()
        away_info = extract_info_team(game_data, home_team=False)
        [print(line) for line in format_info_team(away_info)]
        print("\n")
        print("  ", extract_teams_data(game_data)["home"], sep="")
        print()
        home_info = extract_info_team(game_data, home_team=True)
        [print(line) for line in format_info_team(home_info)]
        print()
        box_info = extract_info_box(game_data)
        [print(line) for line in format_info_box(box_info)]
        print("\n")


if __name__ == "__main__":
    main()
