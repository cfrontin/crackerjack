
import os.path
from pprint import pprint

import boxscore_cli.boxscore as boxscore
import boxscore_cli.tools_mlbapi as tools_mlbapi

def main():

    season = 2023

    mlbam_schedule_url = tools_mlbapi._MLB_SCHEDULE_FORMAT_STRING % (f"{season}-01-01",f"{season}-12-31",)
    sched_data = tools_mlbapi.download_json_url(
        mlbam_schedule_url,
        # debug_file_loader=os.path.join(tools_mlbapi._PKG_DIR, "schedule.json"),
    )

    gamecount_by_date = {}
    games_by_date = {}

    for date in sched_data["dates"]:
        date_of_games = date["date"]

        total_games = 0
        scheduled_games = 0
        cancelled_games = 0
        imminent_games = 0
        completed_games = 0
        inprogress_games = 0
        postponed_games = 0

        games_today = {"scheduled": [], "imminent": [], "cancelled": [], "postponed": [], "inprogress": [], "completed": []}

        for game in date["games"]:
            gamePk = game.get("gamePk")
            gameType = game.get("gameType")
            status = game.get("status")
            statusCode = status.get("statusCode") if status is not None else None
            codedGameState = status.get("codedGameState") if status is not None else None

            total_games += 1
            if codedGameState == "F":
                completed_games += 1
                games_today["completed"].append(gamePk)
            elif codedGameState == "C":
                cancelled_games += 1
                games_today["cancelled"].append(gamePk)
            elif codedGameState == "D":
                postponed_games += 1
                games_today["postponed"].append(gamePk)
            elif codedGameState == "P":
                imminent_games += 1
                games_today["imminent"].append(gamePk)
            elif codedGameState == "S":
                scheduled_games += 1
                games_today["scheduled"].append(gamePk)
            elif codedGameState == "I":
                inprogress_games += 1
                games_today["inprogress"].append(gamePk)
            elif codedGameState is not None:
                raise NotImplementedError(f"codedGameState: {codedGameState} not yet handled.")

        gamecount_by_date[date_of_games] = {
            "total": total_games,
            "scheduled": scheduled_games,
            "cancelled": cancelled_games,
            "imminent": imminent_games,
            "completed": completed_games,
            "inprogress": inprogress_games,
            "postponed": postponed_games,
        }

        games_by_date[date_of_games] = games_today

    gamecount_by_date = dict(sorted(gamecount_by_date.items()))
    days_with_completed = [key for key, value in gamecount_by_date.items() if value["completed"]]
    last_day_completed = days_with_completed[-1]

    for gamePk in games_by_date[last_day_completed]["completed"]:
        print(f"gamePk: {gamePk}")
        boxscore.print_linescore(gamePk, debug=False, wide=False)

if __name__ == "__main__":
    main()

