# boxscore-cli

A CLI boxscore generator.

The newspaper boxscore was basically a perfect way to aggregate data about a given day's games.

Nowadays, nobody reads physical papers anymore, but nerds still use command line interfaces; if there was ever a second-best place for a boxscore, it was a CLI.

## Installation

Dependencies:

  - none, so far

Instructions:

  - navigate to the directory you want to install into
  - activate a virtual environment (if desired; e.g. `conda activate boxscore-env`)
  - `git clone git@github.com:cfrontin/boxscore-cli.git`
  - run `cd boxscore-cli && pip install -e .`
  - navigate out of the installation directory and its parent then make sure `boxscore` runs
  - voilá

## Operation (beta mode)

Currently, the front-end isn't built out, so box scores for games have to be requested manually by their MLB primary key (`gamePk`).
These are 6-digit (occasionally fewer) integer codes that are unique to each game.
They can be found in the MLB GameDay urls, i.e. `718298` in [this box score](https://www.mlb.com/gameday/orioles-vs-braves/2023/05/05/718298/final/box):
```
https://www.mlb.com/gameday/orioles-vs-braves/2023/05/05/718298/final/box
```

To get a line score, type:
```
boxscore --game {gamePk} --line
```
replacing `{gamePk}` with that of the game of your choice.
Likewise, to get a box score, type:
```
boxscore --game {gamePk} --box
```

Without `--line` or `--box` you'll get debugging output for the time being.
In the future this should print the box by default.

Using `--debug` will attempt to read a file `{gamePk}.json` in the install directory rather than making a request to the MLB servers.
