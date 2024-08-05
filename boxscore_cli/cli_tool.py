import pprint
import inquirer
from datetime import datetime

from sparkline import run_sparkline

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
                    "today",
                    "yesterday",
                    ("specified date", "date"),
                ],
            )
            print(f"DEBUG!!!!! date: {date}")
            if date == "date":
                raise NotImplementedError(
                    f"date specification for linescores has not been implemented yet!"
                )
            elif date == "today":
                print("DEBUG!!!!! PRINT TODAY'S LINESCORES")
            elif date == "yesterday":
                print("DEBUG!!!!! PRINT YESTERDAY'S LINESCORES")
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
            raise NotImplementedError(f"mode {mode} has not been implemented yet!")

        elif mode == "standings_wc":
            raise NotImplementedError(f"mode {mode} has not been implemented yet!")

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
