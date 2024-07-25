import os.path
from datetime import datetime, timedelta

import argparse
from pprint import pprint
from re import S

import numpy as np
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

# create a list of the teams for a wildcard printout
wc_list = []
for lg_id, league_data in league_map.items():
    lg_name = league_data["abbrev"]

    mlbam_standings_url = tools_mlbapi._MLB_STANDINGS_FORMAT_STRING % league_data["id"]
    standings_data = tools_mlbapi.download_json_url(
        mlbam_standings_url,
    )

    for record_div in standings_data["records"]:

        id_div = record_div['division']['id']

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
                "rs_team": rs_team,
                "ra_team": ra_team,
                "rd_team": rs_team - ra_team,
            })


# create and sort standings dataframe
df_standings = pd.DataFrame(wc_list)
df_standings.sort_values("wpct", ascending=False, inplace=True)
df_standings.drop(columns=["id", "lg_id", "div_id",], inplace=True)
# df_standings.drop(columns=["id", "lg_id", "div_id", "lg_name",], inplace=True)

# rename to final header names
df_standings.rename(
    columns={
        'name': 'TEAM',
        'wins': 'W',
        'losses': 'L',
        'wpct': 'PCT',
        'wcgb': 'WCGB',
        'streak': 'STRK',
        'rs_team': 'RS',
        'ra_team': 'RA',
        'div_name': 'DIV',
        'div_rank': 'RK',
    },
    inplace=True,
)

# title to length of field map
char_dict = {
    "TEAM": 21,
    "W": 3,
    "L": 3,
    "PCT": 5,
    "WCGB": 5,
    "STRK": 4,
    "RS": 4,
    "RA": 4,
    "DIV": 3,
}

# create the lines for the standings display
sep_line = "•"
head_line = "•"
lg_lines = {
    "AL": {
        "head": "•",
        "leader_lines": ["•"]*3,
        "wc_lines": ["•"]*12,
    },
    "NL": {
        "head": "•",
        "leader_lines": ["•"]*3,
        "wc_lines": ["•"]*12,
    },
}

# make the pct pretty
df_standings.PCT = [f"{np.round(v,3):5.03f}" for v in df_standings.PCT]
df_standings.DIV= df_standings.DIV.str[3:].str[0].str.cat(df_standings.RK.astype(str))

# loop over the dictionary of columns
for k, v in char_dict.items():
    head_line += " "
    sep_line += "•"
    for lg in ["AL", "NL"]:
        lg_lines[lg]["head"] += " " # if k == "TEAM" else "•"
        for idx, row in df_standings[(df_standings['lg_name'].str.upper() == lg) & (df_standings['RK'] == 1)].reset_index().iterrows():
            lg_lines[lg]["leader_lines"][idx] += " "
        for idx, row in df_standings[(df_standings['lg_name'].str.upper() == lg) & (df_standings['RK'] != 1)].reset_index().iterrows():
            lg_lines[lg]["wc_lines"][idx] += " "
            
    head_line += f"{k:>{v}s}"
    sep_line += "•"*v
    for lg in ["AL", "NL"]:
        if k == "TEAM":
            lg_lines[lg]["head"] += f"{'AMERICAN LEAGUE' if lg == 'AL' else 'NATIONAL LEAGUE':<{v}s}"
        else:
            lg_lines[lg]["head"] += f"{k:>{v}s}" # " "*v
        for idx, row in df_standings[(df_standings['lg_name'].str.upper() == lg) & (df_standings['RK'] == 1)].reset_index().iterrows():
            lg_lines[lg]["leader_lines"][idx] += f"{row[k]:>{v}}"
        for idx, row in df_standings[(df_standings['lg_name'].str.upper() == lg) & (df_standings['RK'] != 1)].reset_index().iterrows():
            lg_lines[lg]["wc_lines"][idx] += f"{row[k]:>{v}}"
    
    head_line += " •"
    sep_line += "••"
    for lg in ["AL", "NL"]:
        lg_lines[lg]["head"] += " •" if k == "TEAM" else " •"
        for idx, row in df_standings[(df_standings['lg_name'].str.upper() == lg) & (df_standings['RK'] == 1)].reset_index().iterrows():
                lg_lines[lg]["leader_lines"][idx] += " •"
        for idx, row in df_standings[(df_standings['lg_name'].str.upper() == lg) & (df_standings['RK'] != 1)].reset_index().iterrows():
                lg_lines[lg]["wc_lines"][idx] += " •"

# make a wildcard standings printout

print()
print(sep_line)
print(lg_lines["AL"]["head"])
print(sep_line)
for line in lg_lines["AL"]["leader_lines"]:
    print(line)
print(sep_line)
for line in lg_lines["AL"]["wc_lines"]:
    print(line)
print(sep_line)
print()
print(sep_line)
print(lg_lines["NL"]["head"])
print(sep_line)
for line in lg_lines["NL"]["leader_lines"]:
    print(line)
print(sep_line)
for line in lg_lines["NL"]["wc_lines"]:
    print(line)
print(sep_line)
print()

