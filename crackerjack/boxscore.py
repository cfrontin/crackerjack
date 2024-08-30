#!/usr/bin/env python3

import argparse

from crackerjack.tools_mlbapi import *
from crackerjack.tools_linescore import *
from crackerjack.tools_boxscore import *
from crackerjack.tools_boxscore import *
from crackerjack.extractors_boxscore import *
from crackerjack.formatters_linescore import *
from crackerjack.formatters_boxscore import *


def print_linescore(gamePk, debug=False, wide=False):
    game_data = download_game_data(gamePk, debug=debug)
    dense_lines, _ = format_linescore(
        extract_linescore_innings(game_data),
        extract_teams_data(game_data),
        venue=extract_venue_name(game_data),
        decision_dict=extract_decisions(game_data),
        wide_display=wide,
    )
    print()
    [print(line) for line in dense_lines]
    print()


def do_box(gamePk, debug=False, wide=False):
    game_data = download_game_data(gamePk, debug=debug)
    # print("\n")
    print(extract_gamedate(game_data))
    print(extract_venue_name(game_data))
    print()
    lines_dense, lines_sparse = format_linescore(
        extract_linescore_innings(game_data),
        extract_teams_data(game_data),
        use_top_spacing_line=False,
        use_bottom_spacing_line=False,
        horz_char=" ",
        vert_char=" ",
        cross_char=" ",
        wide_display=wide,
    )
    do_dense = True
    if do_dense:
        [print(line) for line in lines_dense]
    else:
        [print(line) for line in lines_sparse]
    print()
    batter_list = extract_boxscore_batter(game_data)
    pitcher_list = extract_boxscore_pitcher(game_data)
    line_batters_dict = format_batters(batter_list, wide_display=wide)
    line_pitchers_dict = format_pitchers(pitcher_list, wide_display=wide)
    for tmkey in ("away", "home"):
        print("  ", extract_teams_data(game_data)[tmkey], sep="")
        print()
        [print(x) for x in line_batters_dict[tmkey]]
        print()
        [print(x) for x in line_pitchers_dict[tmkey]]
        print()
        info_line_tmkey = extract_info_team(game_data, home_team=(tmkey == "home"))
        [print(x) for x in format_info_team(info_line_tmkey, wide_display=wide)]
        print()
    info_line_box = extract_info_box(game_data)
    [print(x) for x in format_info_box(info_line_box, wide_display=wide)]
    print()


def main():
    ### parse CLI arguments

    parser = argparse.ArgumentParser(
        prog="boxscore",
        description="cfrontin's CLI boxscore and linescore printer",
        epilog="strike three!\a\n",
    )
    parser.add_argument("-l", "--line", action="store_true", default=False)
    parser.add_argument("-b", "--box", action="store_true", default=False)
    parser.add_argument("-g", "--game", action="store", default=None, type=int)
    parser.add_argument("-w", "--wide", action="store_true", default=False)
    parser.add_argument("--debug", action="store_true", default=False)

    args = parser.parse_args()

    ### do functionality

    if args.line:
        print_linescore(args.game, debug=args.debug, wide=args.wide)

    if args.box:
        print()
        do_box(args.game, args.debug)

    # if args.game and (not args.line) and (not args.box):  # exploration mode
    #     game_data = download_game_data(args.game, debug=args.debug)
    #     print()
    #     pp.pprint(game_data, compact=True, indent=1, depth=2)
    #     # print()
    #     # pp.pprint(extract_linescore_data(game_data), compact=True, indent=1, depth=2)
    #     # print()
    #     # print(extract_teams_data(game_data)["away"])
    #     # print(extract_teams_data(game_data)["home"])
    #     # print()
    #     # print(extract_linescore_innings(game_data))
    #     # print()
    #     # print([x.get_appetite() for x in extract_linescore_innings(game_data)])
    #     # print()
    #     # lines_dense, lines_sparse = format_linescore(
    #     #     extract_linescore_innings(game_data),
    #     #     extract_teams_data(game_data),
    #     #     venue=extract_venue_name(game_data),
    #     #     decision_dict=extract_decisions(game_data),
    #     # )
    #     # print("dense linescore:\n")
    #     # [print(x) for x in lines_dense]
    #     # print()
    #     # print("sparse linescore:\n")
    #     # [print(x) for x in lines_sparse]
    #     # print()
    #     # print(translate_gamepk2url(args.game))
    #     # print()
    #     # print(extract_decisions(game_data))
    #     # print()
    #     print()
    #     pp.pprint(extract_boxscore_data(game_data), compact=True, indent=1, depth=2)
    #     print("\n")
    #     print(extract_gamedate(game_data))
    #     print(extract_venue_name(game_data))
    #     print()
    #     lines_dense, lines_sparse = format_linescore(
    #         extract_linescore_innings(game_data),
    #         extract_teams_data(game_data),
    #         use_top_spacing_line=False,
    #         use_bottom_spacing_line=False,
    #         horz_char=" ",
    #         vert_char=" ",
    #         cross_char=" ",
    #     )
    #     do_dense = True
    #     if do_dense:
    #         [print(line) for line in lines_dense]
    #     else:
    #         [print(line) for line in lines_sparse]
    #     print()
    #     print("  ", extract_teams_data(game_data)["away"], sep="")
    #     print()
    #     away_info = extract_info_team(game_data, home_team=False)
    #     [print(line) for line in format_info_team(away_info)]
    #     print("\n")
    #     print("  ", extract_teams_data(game_data)["home"], sep="")
    #     print()
    #     home_info = extract_info_team(game_data, home_team=True)
    #     [print(line) for line in format_info_team(home_info)]
    #     print()
    #     box_info = extract_info_box(game_data)
    #     [print(line) for line in format_info_box(box_info)]
    #     print("\n")


if __name__ == "__main__":
    main()
