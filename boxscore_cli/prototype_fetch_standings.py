import os.path
from datetime import datetime, timedelta

import argparse
from pprint import pprint
from re import S

import pandas as pd

from colorama import Fore, Back, Style

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

wc_list = []

for lg_id, league_data in league_map.items():
    lg_name = league_data["abbrev"]

    mlbam_standings_url = tools_mlbapi._MLB_STANDINGS_FORMAT_STRING % league_data["id"]
    standings_data = tools_mlbapi.download_json_url(
        mlbam_standings_url,
    )

    for record_div in standings_data["records"]:

        id_div = record_div['division']['id']
        print(f"{division_map[id_div]["shortname"]}")

        for rank_tm, record_tm in enumerate(record_div["teamRecords"]):

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

            wc_list.append({
                "name": name_team,
                "id": id_team,
                "wins": wins_team,
                "losses": losses_team,
                "wpct": wpct_team,
                "wcgb": wcgb_team,
                "streak": streak_team,
                "lg_id": lg_id,
                "div_id": id_div,
                "lg_name": lg_name,
                "div_name": division_map[id_div]["shortname"],
                "div_rank": rank_tm+1,
            })

            print(f"\t{name_team}")
            print(
                f"\t\tWINS: {Fore.GREEN}{wins_team:3d}{Fore.RESET}; "
                + f"LOSSES: {Fore.RED}{losses_team:3d}{Fore.RESET}; "
                + f"WPCT: {wpct_team:4.03f}; "
                + f"STREAK: {Fore.GREEN if streak_team.startswith("W") else Fore.RED if streak_team.startswith("L") else Fore.RESET}{streak_team:3s}{Fore.RESET}\n"
                + f"\t\tGB: {gb_team:4s}; "
                + f"WCGB: {wcgb_team:4s}; "
                + f"RS: {rs_team:4d}; "
                + f"RA: {ra_team:4d}; "
                + f"RD: {(rs_team - ra_team):4d}"
            )

        print()

df_standings = pd.DataFrame(wc_list)
df_standings.sort_values("wpct", ascending=False, inplace=True)

for lg in ["AL", "NL"]:
  print(df_standings[(df_standings["lg_name"] == lg) & (df_standings["div_rank"] == 1)])
  print()
  print(df_standings[(df_standings["lg_name"] == lg) & (df_standings["div_rank"] != 1)])
  print()
