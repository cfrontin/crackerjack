import sys

from datetime import datetime
import pprint

from crackerjack.boxscore import do_box
import inquirer
import signal

from crackerjack.fetch_schedule import get_daily_linescores
from crackerjack.fetch_schedule import get_daily_games
from crackerjack.fetch_standings import run_standings
from crackerjack.fetch_standings import run_wildcard
from crackerjack.sparkline import run_sparkline


def ctrlc_handler(sig, frame):
    print("\n\nGet up! Get up! Get outta here! GONE!\n\t-Bob Uecker\n")
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
signal.signal(signal.SIGINT, ctrlc_handler)

print_wide = False


def main():
    while True:
        mode = inquirer.list_input(
            message="Welcome to crackerjack. What would you like to view?",
            choices=[
                "linescores",
                # ("all boxscores", "boxscores"),
                ("a specific boxscore", "boxscore"),
                ("divisional standings", "standings_div"),
                ("league standings", "standings_lg"),
                "sparklines",
                ("the command line (exit)", "exit"),
            ],
        )

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

                get_daily_linescores(
                    fetch_today=False,
                    fetch_yesterday=False,
                    fetch_target_date=date,
                    print_wide=print_wide,
                )
            elif date == "today":
                get_daily_linescores(
                    fetch_today=True,
                    fetch_yesterday=False,
                    print_wide=print_wide,
                )
            elif date == "yesterday":
                get_daily_linescores(
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
            date = inquirer.list_input(
                message="Which day do you want to retrive a boxscore for?",
                choices=[
                    "yesterday",
                    "today",
                    ("specified date", "date"),
                ],
            )
            if date == "date":
                date = get_date()

                games_to_do = get_daily_games(
                    fetch_today=False,
                    fetch_yesterday=False,
                    fetch_target_date=date,
                )
            elif date == "today":
                games_to_do = get_daily_games(
                    fetch_today=True,
                    fetch_yesterday=False,
                )
            elif date == "yesterday":
                games_to_do = get_daily_games(
                    fetch_today=False,
                    fetch_yesterday=True,
                )
            else:
                raise NotImplementedError(
                    f"boxscore date option {date} has not been implemented yet!"
                )

            gamePk = inquirer.list_input(
                message="Which game do you want to retrive a boxscore for?",
                choices=games_to_do["completed"],
            )

            do_box(gamePk)

        elif mode == "standings_div":
            run_standings()

        elif mode == "standings_lg":
            run_wildcard()

        elif mode == "sparklines":
            print()
            run_sparkline()
            print()

        elif mode == "exit":
            print("It might be, it could be, it is! A home run!\n\t-Harry Caray\n")
            sys.exit(0)

        else:
            raise NotImplementedError(f"mode {mode} has not been implemented yet!")


if __name__ == "__main__":
    main()
