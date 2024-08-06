import os.path
from datetime import datetime, timedelta

import argparse
from pprint import pprint
from re import S

from colorama import Fore, Back, Style

# import boxscore_cli.boxscore as boxscore
import boxscore_cli.tools_mlbapi as tools_mlbapi

from boxscore_cli.formatters_boxscore import _CLI_LINE_LENGTH_DEFAULT
from boxscore_cli.formatters_boxscore import _CLI_LINE_LENGTH_WIDE_DEFAULT
from boxscore_cli.tools_mlbapi import _MLB_TEAM_GAMES_FORMAT_STRING

from boxscore_cli.team_lookup import team_list


def run_sparkline(season=datetime.now().year):

    team_output = []

    print("gathering sparklines...", end="", flush=True)
    for id_team, team_data in team_list.items():

        team_games_data = tools_mlbapi.download_json_url(
            _MLB_TEAM_GAMES_FORMAT_STRING % (id_team, season),
        )

        game_count = 0
        wins_vec = []
        for date_data in team_games_data["dates"]:
            for game_data in date_data["games"]:
                if game_data["gameType"] != "R":
                    # print("DEBUG!!!!! skipping non-regular game")
                    continue
                if game_data["status"]["statusCode"] != "F":
                    # print("DEBUG!!!!! skipping non-final game")
                    continue
                game_count += 1

                if game_data["teams"]["home"]["team"]["id"] == id_team:
                    wins_vec.append(game_data["teams"]["home"]["isWinner"])
                    # print("DEBUG!!!!! home game")
                elif game_data["teams"]["away"]["team"]["id"] == id_team:
                    wins_vec.append(game_data["teams"]["away"]["isWinner"])
                    # print("DEBUG!!!!! away game")
                else:
                    assert False

        wins = sum(wins_vec)
        losses = sum([not v for v in wins_vec])
        wpct = wins / (wins + losses)

        # char_available = _CLI_LINE_LENGTH_DEFAULT - 2
        char_available = _CLI_LINE_LENGTH_WIDE_DEFAULT - 2

        if char_available > len(wins_vec):
            output_lines = (
                f"{team_data["abbreviation"]:>3s} "
                + f"{sum(wins_vec)}-{sum([not v for v in wins_vec])}:\n"
            )

            sparkline = (
                "".join([Fore.GREEN + "^" if v else Fore.RED + "v" for v in wins_vec])
                + Fore.RESET
            )
            output_lines += f"  {sparkline:>{char_available}s}"
        else:
            wins_vec_working = wins_vec.copy()

            output_lines = (
                f"{team_data["abbreviation"]:>4s} "
                + f"{sum(wins_vec)}-{sum([not v for v in wins_vec])}:\n"
            )

            char_available -= 3
            sparkline = (
                "..."
                + "".join(
                    [
                        Fore.GREEN + "^" if v else Fore.RED + "v"
                        for v in wins_vec[-char_available:]
                    ]
                )
                + Fore.RESET
            )
            output_lines += f"  {sparkline:>{char_available}s}"

        team_output.append(
            {
                "abbrev": team_data["abbreviation"],
                "wpct": wpct,
                "output": output_lines,
            }
        )
    print(" done!\n", flush=True)

    team_output = list(sorted(team_output, key=lambda v: v["wpct"], reverse=True))

    for v in team_output:
        print(v["output"])


if __name__ == "__main__":
    run_sparkline()
