#!/usr/bin/env python3

import os.path
import argparse


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

    ### parse CLI arguments

    parser= argparse.ArgumentParser(
            prog="boxscore",
            description="cfrontin's CLI boxscore and linescore printer",
            epilog="strike three!\a\n",
            )
    parser.add_argument("-l", "--line", action="store_true", default=False)
    parser.add_argument("-b", "--box", action="store_true", default=False)

    args, arg_filenames = parser.parse_known_args()

    ### do functionality

    if args.line:
        print_dummy_linescore()

    if args.box:
        print_dummy_boxscore()

if __name__ == "__main__":
    main()
