import os.path
from datetime import datetime, timedelta

import argparse
from pprint import pprint

import boxscore_cli.team_lookup
import boxscore_cli.boxscore as boxscore
import boxscore_cli.tools_mlbapi as tools_mlbapi


def get_daily_games(
    season=datetime.today().year,
    fetch_today=True,
    fetch_yesterday=False,
    fetch_target_date=False,
    # print_wide=False,
):

    # override season if user requests a specific date
    if fetch_target_date:
        assert not fetch_today and not fetch_yesterday
        season = datetime.strptime(fetch_target_date, "%Y-%m-%d").year

    mlbam_schedule_url = tools_mlbapi._MLB_SCHEDULE_FORMAT_STRING % (
        f"{season}-01-01",
        f"{season}-12-31",
    )
    sched_data = tools_mlbapi.download_json_url(
        mlbam_schedule_url,
        # debug_file_loader=os.path.join(tools_mlbapi._PKG_DIR, "schedule.json"),
    )

    gamecount_by_date = {}
    games_by_date = {}

    today = None
    yesterday = None
    tgt_day = None

    for date in sched_data["dates"]:
        date_of_games = date["date"]
        is_today = (
            datetime.strptime(date_of_games, "%Y-%m-%d").date()
            == datetime.today().date()
        )
        is_yesterday = (
            datetime.strptime(date_of_games, "%Y-%m-%d").date()
            == (datetime.today() - timedelta(days=1)).date()
        )
        is_tgt_day = fetch_target_date and (
            datetime.strptime(date_of_games, "%Y-%m-%d").date()
            == (datetime.strptime(fetch_target_date, "%Y-%m-%d").date())
        )

        total_games = 0
        scheduled_games = 0
        cancelled_games = 0
        imminent_games = 0
        completed_games = 0
        inprogress_games = 0
        postponed_games = 0

        games_thisday = {
            "scheduled": [],
            "imminent": [],
            "cancelled": [],
            "postponed": [],
            "inprogress": [],
            "completed": [],
        }

        for game in date["games"]:
            gamePk = game.get("gamePk")
            gameType = game.get("gameType")
            status = game.get("status")
            statusCode = status.get("statusCode") if status is not None else None
            codedGameState = (
                status.get("codedGameState") if status is not None else None
            )

            # get a quick description of the game
            teamID_away = int(game["teams"]["away"]["team"]["id"])
            teamID_home = int(game["teams"]["home"]["team"]["id"])
            if teamID_away in boxscore_cli.team_lookup.team_list.keys():
                threeletter_away = boxscore_cli.team_lookup.team_list[
                    int(game["teams"]["away"]["team"]["id"])
                ].get("abbreviation")
            else:
                threeletter_away = "XXX"  # DEBUG!!!!!
            if teamID_home in boxscore_cli.team_lookup.team_list.keys():
                threeletter_home = boxscore_cli.team_lookup.team_list[
                    int(game["teams"]["home"]["team"]["id"])
                ].get("abbreviation")
            else:
                threeletter_home = "XXX"  # DEBUG!!!!!
            game_summary_string = f"{threeletter_away} @ {threeletter_home}"

            total_games += 1
            if codedGameState == "F":
                completed_games += 1
                games_thisday["completed"].append((game_summary_string, gamePk))
            elif codedGameState == "O":
                completed_games += 1
                games_thisday["completed"].append((game_summary_string, gamePk))
            elif codedGameState == "C":
                cancelled_games += 1
                games_thisday["cancelled"].append((game_summary_string, gamePk))
            elif codedGameState == "D":
                postponed_games += 1
                games_thisday["postponed"].append((game_summary_string, gamePk))
            elif codedGameState == "P":
                imminent_games += 1
                games_thisday["imminent"].append((game_summary_string, gamePk))
            elif codedGameState == "S":
                scheduled_games += 1
                games_thisday["scheduled"].append((game_summary_string, gamePk))
            elif codedGameState == "I":
                inprogress_games += 1
                games_thisday["inprogress"].append((game_summary_string, gamePk))
            elif codedGameState == "U":
                inprogress_games += 1
                games_thisday["inprogress"].append((game_summary_string, gamePk))
            elif codedGameState is not None:
                raise NotImplementedError(
                    f"codedGameState: {codedGameState} not yet handled."
                )

        gamecount_by_date[date_of_games] = {
            "total": total_games,
            "scheduled": scheduled_games,
            "cancelled": cancelled_games,
            "imminent": imminent_games,
            "completed": completed_games,
            "inprogress": inprogress_games,
            "postponed": postponed_games,
        }

        games_by_date[date_of_games] = games_thisday

        if is_today and completed_games > 0:
            today = games_thisday
        if is_yesterday and completed_games > 0:
            yesterday = games_thisday
        if is_tgt_day and completed_games > 0:
            tgt_day = games_thisday

    gamecount_by_date = dict(sorted(gamecount_by_date.items()))
    days_with_completed = [
        key for key, value in gamecount_by_date.items() if value["completed"]
    ]
    last_day_completed = days_with_completed[-1]

    if fetch_yesterday:
        return yesterday

    if fetch_today:
        return today

    if fetch_target_date:
        return tgt_day

    return None


def get_daily_linescores(
    season=datetime.today().year,
    fetch_today=True,
    fetch_yesterday=False,
    fetch_target_date=False,
    print_wide=False,
):

    # override season if user requests a specific date
    if fetch_target_date:
        assert not fetch_today and not fetch_yesterday
        season = datetime.strptime(fetch_target_date, "%Y-%m-%d").year

    mlbam_schedule_url = tools_mlbapi._MLB_SCHEDULE_FORMAT_STRING % (
        f"{season}-01-01",
        f"{season}-12-31",
    )
    sched_data = tools_mlbapi.download_json_url(
        mlbam_schedule_url,
        # debug_file_loader=os.path.join(tools_mlbapi._PKG_DIR, "schedule.json"),
    )

    gamecount_by_date = {}
    games_by_date = {}

    today = None
    yesterday = None
    tgt_day = None

    for date in sched_data["dates"]:
        date_of_games = date["date"]
        is_today = (
            datetime.strptime(date_of_games, "%Y-%m-%d").date()
            == datetime.today().date()
        )
        is_yesterday = (
            datetime.strptime(date_of_games, "%Y-%m-%d").date()
            == (datetime.today() - timedelta(days=1)).date()
        )
        is_tgt_day = fetch_target_date and (
            datetime.strptime(date_of_games, "%Y-%m-%d").date()
            == (datetime.strptime(fetch_target_date, "%Y-%m-%d").date())
        )

        total_games = 0
        scheduled_games = 0
        cancelled_games = 0
        imminent_games = 0
        completed_games = 0
        inprogress_games = 0
        postponed_games = 0

        games_thisday = {
            "scheduled": [],
            "imminent": [],
            "cancelled": [],
            "postponed": [],
            "inprogress": [],
            "completed": [],
        }

        for game in date["games"]:
            gamePk = game.get("gamePk")
            gameType = game.get("gameType")
            status = game.get("status")
            statusCode = status.get("statusCode") if status is not None else None
            codedGameState = (
                status.get("codedGameState") if status is not None else None
            )

            total_games += 1
            if codedGameState == "F":
                completed_games += 1
                games_thisday["completed"].append(gamePk)
            elif codedGameState == "O":
                completed_games += 1
                games_thisday["completed"].append(gamePk)
            elif codedGameState == "C":
                cancelled_games += 1
                games_thisday["cancelled"].append(gamePk)
            elif codedGameState == "D":
                postponed_games += 1
                games_thisday["postponed"].append(gamePk)
            elif codedGameState == "P":
                imminent_games += 1
                games_thisday["imminent"].append(gamePk)
            elif codedGameState == "S":
                scheduled_games += 1
                games_thisday["scheduled"].append(gamePk)
            elif codedGameState == "I":
                inprogress_games += 1
                games_thisday["inprogress"].append(gamePk)
            elif codedGameState == "U":
                inprogress_games += 1
                games_thisday["inprogress"].append(gamePk)
            elif codedGameState is not None:
                raise NotImplementedError(
                    f"codedGameState: {codedGameState} not yet handled."
                )

        gamecount_by_date[date_of_games] = {
            "total": total_games,
            "scheduled": scheduled_games,
            "cancelled": cancelled_games,
            "imminent": imminent_games,
            "completed": completed_games,
            "inprogress": inprogress_games,
            "postponed": postponed_games,
        }

        games_by_date[date_of_games] = games_thisday

        if is_today and completed_games > 0:
            today = games_thisday
        if is_yesterday and completed_games > 0:
            yesterday = games_thisday
        if is_tgt_day and completed_games > 0:
            tgt_day = games_thisday

    gamecount_by_date = dict(sorted(gamecount_by_date.items()))
    days_with_completed = [
        key for key, value in gamecount_by_date.items() if value["completed"]
    ]
    last_day_completed = days_with_completed[-1]

    if fetch_yesterday:
        print("YESTERDAY'S GAMES:\n")
        if yesterday is None:
            print("No games completed yesterday.\n")
        else:
            for gamePk in yesterday["completed"]:
                print(f"gamePk: {gamePk}")
                boxscore.print_linescore(gamePk, debug=False, wide=print_wide)

    if fetch_today:
        print("TODAY'S GAMES:\n")
        if today is None:
            print("No games completed yet today.\n")
        else:
            for gamePk in today["completed"]:
                print(f"gamePk: {gamePk}")
                boxscore.print_linescore(gamePk, debug=False, wide=print_wide)

    if fetch_target_date:
        print(f"GAMES ON {fetch_target_date}:\n")
        if tgt_day is None:
            print(f"No games completed on {fetch_target_date}.\n")
        else:
            for gamePk in tgt_day["completed"]:
                print(f"gamePk: {gamePk}")
                boxscore.print_linescore(gamePk, debug=False, wide=print_wide)

    if (not fetch_today) and (not fetch_yesterday) and (not fetch_target_date):
        for gamePk in games_by_date[last_day_completed]["completed"]:
            print(f"gamePk: {gamePk}")
            boxscore.print_linescore(gamePk, debug=False, wide=print_wide)


def main():
    ### parse CLI arguments

    parser = argparse.ArgumentParser(
        prog="fetchscores",
        description="cfrontin's CLI boxscore and linescore printer",
        epilog="strike three!\a\n",
    )
    parser.add_argument("-t", "--today", action="store_true", default=False)
    parser.add_argument("-y", "--yesterday", action="store_true", default=False)
    parser.add_argument("-w", "--wide", action="store_true", default=False)
    parser.add_argument("--debug", action="store_true", default=False)

    args = parser.parse_args()

    get_daily_linescores(fetch_today=args.today, fetch_yesterday=args.yesterday)


if __name__ == "__main__":
    main()
