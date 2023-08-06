
from collections import OrderedDict

import tools_mlbapi
from tools_boxscore import *

# this should be reconfigured to be part of a settings file
_CLI_LINE_LENGTH_DEFAULT = 80

def format_pitchers(
    pitcher_list: dict[str : list[BoxScorePitcher]],
    indent_size=2,
    init_indent=2,
    vert_char="|",
    cross_char="+",
) -> dict[str : dict[str:str]]:
    """
    format one or both teams' pitchers
    """

    stats_appetite = [-1 for x in pitcher_list["away"][0].get_appetite_stats()]
    for tmkey in ("away", "home"):
        for bsr in pitcher_list[tmkey]:
            for idx_stat in range(len(stats_appetite)):
                stats_appetite[idx_stat] = max(
                    [stats_appetite[idx_stat], bsr.get_appetite_stats()[idx_stat]]
                )
    stats_appetite_total = sum(stats_appetite) + (len(stats_appetite) - 1) * len(
        " %s " % vert_char
    )

    staff_to_stats = {
        "away": [],
        "home": [],
    }
    staff_to_bsp = {
        "away": [],
        "home": [],
    }
    lines_out = {
        "away": [],
        "home": [],
    }

    line_output_fmt = ""
    for x in ["%" + str(x) + "s " + vert_char + " " for x in stats_appetite]:
        line_output_fmt += x
    line_output_fmt = line_output_fmt[:-3]
    for tmkey in ("away", "home"):
        for bsp in pitcher_list[tmkey]:
            line_output = line_output_fmt % (
                bsp.innings_pitched,
                bsp.hits,
                bsp.runs,
                bsp.runs_earned,
                bsp.bb,
                bsp.strikeouts,
                bsp.hr,
            )
            staff_to_stats[tmkey].append(line_output)
            staff_to_bsp[tmkey].append(bsp)

    resid_char = (
        _CLI_LINE_LENGTH_DEFAULT - indent_size * init_indent - stats_appetite_total - 4
    )

    for tmkey in ("away", "home"):
        header_line = (
            " " * indent_size * init_indent
            + " " * resid_char
            + " %s  " % vert_char
            + "".join(
                [(x + " %s " % vert_char) for x in BoxScorePitcher.get_header_stats()]
            )[:-3]
        )
        lines_out[tmkey].append(header_line)
        for pitcher_index in range(len(staff_to_stats[tmkey])):
            statline = staff_to_stats[tmkey][pitcher_index]
            prefix_line = " %1d: " % (pitcher_index+1)
            bsp = staff_to_bsp[tmkey][pitcher_index]
            name_sector = "%s%s, %s (#%s)" % (
                prefix_line,
                bsp.lastname_player,
                bsp.firstname_player,
                bsp.jersey_player,
            )
            name_sector_fmt = "%-" + str(resid_char) + "s"
            line = (
                " " * indent_size * init_indent
                + (name_sector_fmt % name_sector)
                + " %s " % vert_char
                + statline
            )
            lines_out[tmkey].append(line)

    return lines_out


def format_batters(
    batter_list: dict[str : list[BoxScoreBatter]],
    indent_size=2,
    init_indent=2,
    vert_char="|",
    cross_char="+",
) -> dict[str : dict[str:str]]:
    """
    format one or both teams' batters
    """

    stats_appetite = [-1 for x in batter_list["away"][0].get_appetite_stats()]
    for tmkey in ("away", "home"):
        for bsr in batter_list[tmkey]:
            for idx_stat in range(len(stats_appetite)):
                stats_appetite[idx_stat] = max(
                    [stats_appetite[idx_stat], bsr.get_appetite_stats()[idx_stat]]
                )
    stats_appetite_total = sum(stats_appetite) + (len(stats_appetite) - 1) * len(
        " %s " % vert_char
    )

    lineups_to_stats = {
        "away": {x: [] for x in range(1, 9 + 1)},
        "home": {x: [] for x in range(1, 9 + 1)},
    }
    lineups_to_bsb = {
        "away": {x: [] for x in range(1, 9 + 1)},
        "home": {x: [] for x in range(1, 9 + 1)},
    }
    lines_out = {
        "away": [],
        "home": [],
    }

    line_output_fmt = ""
    for x in ["%" + str(x) + "s " + vert_char + " " for x in stats_appetite]:
        line_output_fmt += x
    line_output_fmt = line_output_fmt[:-3]
    for tmkey in ("away", "home"):
        for bsb in batter_list[tmkey]:
            line_output = line_output_fmt % (
                bsb.ab,
                bsb.runs,
                bsb.hits,
                bsb.rbi,
                bsb.bb,
                bsb.so,
                bsb.po,
                bsb.asst,
            )
            if bsb.batting_order is None:
                continue  # TODO: debug this case (718360)
            lineup_pos = int(bsb.batting_order[0])
            lineup_count = int(str(bsb.batting_order[1:]))
            assert lineup_pos in lineups_to_stats[tmkey]
            if lineup_count > 0:
                assert len(lineups_to_stats[tmkey][lineup_pos]) == lineup_count
            lineups_to_stats[tmkey][lineup_pos].append(line_output)
            lineups_to_bsb[tmkey][lineup_pos].append(bsb)

    resid_char = (
        _CLI_LINE_LENGTH_DEFAULT - indent_size * init_indent - stats_appetite_total - 4
    )

    for tmkey in ("away", "home"):
        header_line = (
            " " * indent_size * init_indent
            + " " * resid_char
            + " %s " % vert_char
            + "".join(
                [(x + " %s " % vert_char) for x in BoxScoreBatter.get_header_stats()]
            )[:-3]
        )
        lines_out[tmkey].append(header_line)
        for poskey in lineups_to_stats[tmkey]:
            for subno, statline in enumerate(lineups_to_stats[tmkey][poskey]):
                prefix_line = " %1d: " % poskey if subno == 0 else "      "
                bsb = lineups_to_bsb[tmkey][poskey][subno]
                name_sector = "%s%s, %s (#%s), %s" % (
                    prefix_line,
                    bsb.lastname_player,
                    bsb.firstname_player,
                    bsb.jersey_player,
                    bsb.pos,
                )
                name_sector_fmt = "%-" + str(resid_char) + "s"
                line = (
                    " " * indent_size * init_indent
                    + (name_sector_fmt % name_sector)
                    + " %s " % vert_char
                    + statline
                )
                lines_out[tmkey].append(line)

    return lines_out


def format_info_box(
    info_box: OrderedDict[str:list], indent_size=2, init_indent=1
) -> list[str]:
    """
    get lines to print box info

    take the box score info, and make lines to display nicely without overrunning,
    given some indentation specifications
    """

    lines = []

    for key, values in info_box.items():
        working_str = " " * indent_size * init_indent + key + ": "
        for idx_value, value in enumerate(values):
            if (
                len(working_str)
                + len(value)
                + (2 if (idx_value + 1 != len(values)) else 0)
                > _CLI_LINE_LENGTH_DEFAULT
            ):
                lines.append(working_str)
                working_str = (
                    " " * indent_size * (init_indent + 2)
                    + value
                    + ("; " if (idx_value + 1 != len(values)) else "")
                )
            else:
                working_str += value + ("; " if (idx_value + 1 != len(values)) else "")
        lines.append(working_str)

    return lines


def format_info_team(
    info_team: dict[OrderedDict[str:list]],
    indent_size=2,
    init_indent=2,
):
    """
    get lines to print team info

    take the team score info, make lines to display nicely without overrunning,
    given some indentation specifications
    """

    lines = []

    for team_type in tools_mlbapi._MLBAM_TEAM_TYPES:
        if team_type in info_team:
            lines.append(" " * indent_size * init_indent + team_type)

            next_indent = init_indent + 1

            for key, values in info_team[team_type].items():
                working_str = " " * indent_size * next_indent + key + ": "
                for idx_value, value in enumerate(values):
                    if (
                        len(working_str)
                        + len(value)
                        + (2 if (idx_value + 1 != len(values)) else 0)
                        > _CLI_LINE_LENGTH_DEFAULT
                    ):
                        lines.append(working_str)
                        working_str = (
                            " " * indent_size * (next_indent + 2)
                            + value
                            + ("; " if (idx_value + 1 != len(values)) else "")
                        )
                    else:
                        working_str += value + (
                            "; " if (idx_value + 1 != len(values)) else ""
                        )
                lines.append(working_str)

    return lines

