import copy
import re
from collections import OrderedDict

from boxscore_cli.tools_mlbapi import *
import boxscore_cli.tools_mlbapi as tools_mlbapi
from boxscore_cli.tools_boxscore import *


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
        assert info_field["label"] in tools_mlbapi._MLBAM_GAME_LABELS, (
            "%s must be in game labels" % info_field["label"]
        )
        if info_field["label"] in labels_to_skip:
            continue  # skip stuff that should be skipped
        if info_field["value"].endswith("."):
            info_field["value"] = info_field["value"][:-1]  # trim trailing period
        info_field["value"] = [
            x.strip() for x in re.split(";|\.", info_field["value"]) if not x.isspace()
        ]
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
        assert info_title in tools_mlbapi._MLBAM_TEAM_TYPES
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


def extract_boxscore_pitcher(data_game: dict) -> dict[str : list[BoxScorePitcher]]:
    """
    extract each pitcher's line from the game data, return a list for each team
    """

    data_box = extract_boxscore_data(data_game)

    lines_dict = {"away": [], "home": []}

    for tm_key in ("away", "home"):
        for player_key in data_box["teams"][tm_key]["pitchers"]:
            player_key_mod = get_prefixed_player_id(player_key)
            assert player_key_mod in data_box["teams"][tm_key]["players"]

            player_data = extract_player_detailed(data_game, player_key)
            player_game_data = data_box["teams"][tm_key]["players"][player_key_mod]
            player_pitching_data = player_game_data["stats"]["pitching"]

            player_bsp = BoxScorePitcher(
                player_data.get("useLastName"),
                player_data.get("useName"),
                player_game_data.get("jerseyNumber"),
                player_pitching_data.get("inningsPitched"),
                player_pitching_data.get("hits"),
                player_pitching_data.get("runs"),
                player_pitching_data.get("earnedRuns"),
                player_pitching_data.get("baseOnBalls"),
                player_pitching_data.get("strikeOuts"),
                player_pitching_data.get("homeRuns"),
            )

            lines_dict[tm_key].append(player_bsp)

    return lines_dict


def extract_boxscore_batter(data_game: dict) -> dict[str : list[BoxScoreBatter]]:
    """
    extract each batters's line from the game data, return a list for each team
    """

    data_box = extract_boxscore_data(data_game)

    lines_dict = {"away": [], "home": []}

    for tm_key in ("away", "home"):
        for player_key in data_box["teams"][tm_key]["batters"]:
            player_key_mod = get_prefixed_player_id(player_key)
            assert player_key_mod in data_box["teams"][tm_key]["players"]

            player_data = extract_player_detailed(data_game, player_key)
            player_game_data = data_box["teams"][tm_key]["players"][player_key_mod]
            player_batting_data = player_game_data["stats"]["batting"]
            player_fielding_data = player_game_data["stats"]["fielding"]

            player_bsb = BoxScoreBatter(
                player_data.get("useLastName"),
                player_data.get("useName"),
                "-".join(
                    [
                        posi.get("abbreviation")
                        for posi in player_game_data["allPositions"]
                    ]
                ),
                player_game_data.get("jerseyNumber"),
                player_game_data.get("battingOrder"),
                player_batting_data.get("atBats"),
                player_batting_data.get("runs"),
                player_batting_data.get("hits"),
                player_batting_data.get("rbi"),
                player_batting_data.get("baseOnBalls"),
                player_batting_data.get("strikeOuts"),
                player_fielding_data.get("putOuts"),
                player_fielding_data.get("assists"),
            )

            lines_dict[tm_key].append(player_bsb)

    return lines_dict
