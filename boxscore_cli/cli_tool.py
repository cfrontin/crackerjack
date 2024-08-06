import sys

from datetime import datetime
import pprint

import inquirer
import signal

from boxscore_cli.fetch_schedule import get_daily_games
from boxscore_cli.prototype_fetch_standings import run_standings
from boxscore_cli.prototype_fetch_standings import run_wildcard
from boxscore_cli.sparkline import run_sparkline

def signal_handler(sig, frame):
    print("\n\nGet up! Get up! Get outta here! GONE!\n\t-Bob Uecker\n")
    # Perform any cleanup here
    sys.exit(0)


def is_valid_date(date_str):
    """Check if the provided date string is a valid date."""
    try:
        # try to parse the date string
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_date():
    """Prompt the user for a date until a valid date is provided."""
    while True:
        # ask the user for a date
        questions = [inquirer.Text("date", message="Please enter a date (YYYY-MM-DD)")]
        answers = inquirer.prompt(questions)
        date_input = answers["date"]

        # validate the date
        if is_valid_date(date_input):
            print(f"You entered a valid date: {date_input}")
            return date_input
        else:
            print("Invalid date format. Please try again.")

# register the signal handler
signal.signal(signal.SIGINT, signal_handler)

print_wide = False

def cli_loop():
    while True:
        mode = inquirer.list_input(
            message="Welcome to boxscore_cli. What would you like to view?",
            choices=[
                "linescores",
                ("all boxscores", "boxscores"),
                ("a specific boxscore", "boxscore"),
                ("divisional standings", "standings_div"),
                ("league standings", "standings_lg"),
                "sparklines",
                ("the command line (exit)", "exit"),
            ],
        )

        print(f"DEBUG!!!!! mode: {mode}")

        if mode == "linescores":
            date = inquirer.list_input(
                message="Which day do you want to retrive linescores for?",
                choices=[
                    "yesterday",
                    "today",
                    ("specified date", "date"),
                ],
            )
            if date == "date":
                date = get_date()

                get_daily_games(
                    fetch_today=False,
                    fetch_yesterday=False,
                    fetch_target_date=date,
                    print_wide=print_wide,
                )
            elif date == "today":
                get_daily_games(
                    fetch_today=True,
                    fetch_yesterday=False,
                    print_wide=print_wide,
                )
            elif date == "yesterday":
                get_daily_games(
                    fetch_today=False,
                    fetch_yesterday=True,
                    print_wide=print_wide,
                )
            else:
                raise NotImplementedError(
                    f"linescore date option {date} has not been implemented yet!"
                )

        elif mode == "boxscores":
            raise NotImplementedError(f"mode {mode} has not been implemented yet!")

        elif mode == "boxscore":
            date = get_date()
            raise NotImplementedError(f"mode {mode} has not been implemented yet!")

        elif mode == "standings_div":
            run_standings()

        elif mode == "standings_lg":
            run_wildcard()

        elif mode == "sparklines":
            print()
            run_sparkline()
            print()

        elif mode == "exit":
            break

        else:
            raise NotImplementedError(f"mode {mode} has not been implemented yet!")

if __name__ == "__main__":
    cli_loop()
