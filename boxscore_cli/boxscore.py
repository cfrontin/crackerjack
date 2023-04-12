#!/usr/bin/env python3

import os.path

APP_DIR = os.path.split(__file__)[0]

def print_dummy_linescore():

    filename_linescore = os.path.join(APP_DIR, "linescore_dummy.txt")
    with open(filename_linescore, 'r') as f:
        linescore_str = f.read()

    print()
    print(linescore_str)
    print()


def print_dummy_boxscore():

    filename_boxscore = os.path.join(APP_DIR, "boxscore_dummy.txt")
    with open(filename_boxscore, 'r') as f:
        boxscore_str = f.read()

    print()
    print(boxscore_str)
    print()



def main():

    print_dummy_linescore()

    print_dummy_boxscore()

if __name__ == "__main__":
    main()
