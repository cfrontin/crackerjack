# `crackerjack`

[![Cracker Jack surprise inside logo](https://live.staticflickr.com/3662/3331692605_5b0ef798b5_c.jpg?w=400)](https://flickr.com/photos/hermanturnip/3331692605)

A CLI boxscore generator.

The newspaper boxscore was basically a perfect way to aggregate data about a given day's games.

Nowadays, nobody reads physical papers anymore, but nerds still use command line interfaces; if there was ever a second-best place for a boxscore, it was a CLI.

## Installation

Dependencies:

  - setuptools: package development and distribution library 
  - [`inquirer`:](https://python-inquirer.readthedocs.io/en/latest/usage.html) a CLI navigation library
  - [`colorama`:](https://github.com/tartley/colorama) a library for coloring CLI outputs
  - [`numpy`:](https://numpy.org) for numerical computations
  - [`pandas`:](https://pandas.pydata.org/) data loading and analysis

Instructions:

  - navigate to the directory you want to install into
  - activate a virtual environment (if desired; e.g. `conda activate boxscore-env`)
  - `git clone git@github.com:cfrontin/boxscore-cli.git`
    - makes a local copy of the git repository with ties back to the github.com repo
  - `cd boxscore-cli` to move into the directory you just cloned
  - `pip install -e .` to install the package (in editable mode)
  - navigate out of the installation directory and its parent then make sure `boxscore` runs
  - voilá

## Operation (beta mode)

Type `crackerjack` at the command line after installing.

This will drop you into a menu:

![`crackerjack` menu demo](assets/menu_demo.png)

From there, you can navigate to the features of crackerjack.
These are line scores:

![`crackerjack` linescore demo](assets/linescore_demo.png)

Oof. [Tough night for the Red Sox](https://www.youtube.com/watch?v=lGMhfYftFCk).
Also boxscores:

![`crackerjack` boxscore demo](assets/boxscore_demo.png)

There's also standings, and [standings sparklines](https://en.wikipedia.org/wiki/Sparkline):

![`crackerjack` sparklines demo](assets/sparklines_demo.png)
