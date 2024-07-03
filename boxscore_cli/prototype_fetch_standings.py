import os.path
from datetime import datetime, timedelta

import argparse
from pprint import pprint
from re import S

# import boxscore_cli.boxscore as boxscore
import boxscore_cli.tools_mlbapi as tools_mlbapi

from formatters_boxscore import _CLI_LINE_LENGTH_DEFAULT
from formatters_boxscore import _CLI_LINE_LENGTH_WIDE_DEFAULT

league_map = {
  tools_mlbapi._MLBAM_LEAGUEID_AL: {
    "id": tools_mlbapi._MLBAM_LEAGUEID_AL,
    "name": "American",
    "abbrev": "AL",
  },
  tools_mlbapi._MLBAM_LEAGUEID_NL: {
    "id": tools_mlbapi._MLBAM_LEAGUEID_NL,
    "name": "National",
    "abbrev": "NL",
  },
}

division_map = {
  tools_mlbapi._MLBAM_DIVISIONID_AL_WEST: {
    "shortname": "AL West",
    "fullname": "American League West",
  },
  tools_mlbapi._MLBAM_DIVISIONID_AL_EAST: {
    "shortname": "AL East",
    "fullname": "American League East",
  },
  tools_mlbapi._MLBAM_DIVISIONID_AL_CENTRAL: {
    "shortname": "AL Central",
    "fullname": "American League Central",
  },
  tools_mlbapi._MLBAM_DIVISIONID_NL_WEST: {
    "shortname": "NL West",
    "fullname": "National League West",
  },
  tools_mlbapi._MLBAM_DIVISIONID_NL_EAST: {
    "shortname": "NL East",
    "fullname": "National League East",
  },
  tools_mlbapi._MLBAM_DIVISIONID_NL_CENTRAL: {
    "shortname": "NL Central",
    "fullname": "National League Central",
  },
}

for lg_id, league_data in league_map.items():
    lg_name = league_data["abbrev"]

    mlbam_standings_url = tools_mlbapi._MLB_STANDINGS_FORMAT_STRING % league_data["id"]
    standings_data = tools_mlbapi.download_json_url(
        mlbam_standings_url,
    )

    for record_div in standings_data["records"]:

        id_div = record_div['division']['id']
        print(f"{division_map[id_div]["shortname"]}")

        for record_tm in record_div["teamRecords"]:

            name_team = record_tm['team']['name']
            id_team = record_tm['team']['id']

            wins_team = record_tm['wins']
            losses_team = record_tm['losses']
            wpct_team = wins_team/(wins_team+losses_team)
            gb_team = record_tm["gamesBack"]
            wcgb_team = record_tm["wildCardGamesBack"]
            rs_team = record_tm["runsScored"]
            ra_team = record_tm["runsAllowed"]
            streak_team = record_tm["streak"]["streakCode"]

            print(f"\t{name_team}")
            print(
                f"\t\tWINS: {wins_team:3d}; "
                + f"LOSSES: {losses_team:3d}; "
                + f"WPCT: {wpct_team:4.03f}; "
                + f"STREAK: {streak_team:3s}\n"
                + f"\t\tGB: {gb_team:4s}; "
                + f"WCGB: {wcgb_team:4s}; "
                + f"RS: {rs_team:4d}; "
                + f"RA: {ra_team:4d}; "
                + f"RD: {(rs_team - ra_team):4d}"
            )

        print()

