import pprint
import inquirer

mode = inquirer.list_input(
    message="Welcome to boxscore_cli. What would you like to view?",
    choices=[
        "linescores",
        ("all boxscores", "boxscores"),
        ("a specific boxscore", "boxscore"),
        "standings",
    ],
)

print(f"DEBUG!!!!! mode: {mode}")
if mode == "linescores":
    date = inquirer.list_input(
        message="Which day do you want to retrive linescores for?",
        choices=["today", "yesterday", ("specified date", "date"),]
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
        raise NotImplementedError(f"linescore date option {date} has not been implemented yet!") 

else:
    raise NotImplementedError(f"mode {mode} has not been implemented yet!") 

