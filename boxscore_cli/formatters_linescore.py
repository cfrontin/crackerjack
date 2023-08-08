
from boxscore_cli.tools_mlbapi import *
from boxscore_cli.tools_linescore import *

# this should be reconfigured to be part of a settings file
from boxscore_cli.formatters_boxscore import _CLI_LINE_LENGTH_DEFAULT
from boxscore_cli.formatters_boxscore import _CLI_LINE_LENGTH_WIDE_DEFAULT

def format_linescore(
    linescoreinning_list: list[LineScoreInning],
    teams: dict[Team],
    decision_dict=None,
    venue=None,
    cross_char="+",
    vert_char="|",
    horz_char="-",
    min_spaces_dense=2,
    min_spaces_sparse=1,
    indent_dense=0,
    indent_sparse=2,
    force_uppercase_team=True,
    use_top_spacing_line=False,
    use_bottom_spacing_line=False,
    wide_display=False,
) -> list[str]:
    """
    TODO: create this documentation
    """

    # craete the format string
    format_name_dense = ""
    format_name_sparse = ""
    format_line_dense = ""
    format_line_sparse = ""

    # create substitution sets for each line permutation
    substitution_set_name_top_dense = []
    substitution_set_name_away_dense = []
    substitution_set_name_home_dense = []
    substitution_set_name_bot_dense = []
    substitution_set_name_top_sparse = []
    substitution_set_name_away_sparse = []
    substitution_set_name_home_sparse = []
    substitution_set_line_top_dense = []
    substitution_set_line_away_dense = []
    substitution_set_line_home_dense = []
    substitution_set_line_bot_dense = []
    substitution_set_line_top_sparse = []
    substitution_set_line_away_sparse = []
    substitution_set_line_home_sparse = []

    # start a count of the spaces
    spaces_linescore_dense = 0
    spaces_linescore_sparse = 0

    # add the indentation
    spaces_linescore_dense += indent_dense
    format_name_dense += " " * indent_dense
    spaces_linescore_sparse += indent_sparse
    format_name_sparse += " " * indent_sparse

    # add the stuff before the innings
    spaces_linescore_dense += 2  # border char and one space before name
    format_name_dense += "%1s "
    substitution_set_name_top_dense.append(cross_char)
    substitution_set_name_away_dense.append(vert_char)
    substitution_set_name_home_dense.append(vert_char)
    substitution_set_name_bot_dense.append(cross_char)
    spaces_linescore_dense += 3  # border char and one space (at least) after name
    format_line_dense += " %1s "
    substitution_set_line_top_dense.append(cross_char)
    substitution_set_line_away_dense.append(cross_char)
    substitution_set_line_home_dense.append(cross_char)
    substitution_set_line_bot_dense.append(cross_char)
    spaces_linescore_sparse += 2  # border char and one space before name
    format_name_sparse += ""
    spaces_linescore_sparse += 1  # border char and one space (at least) after name
    format_line_sparse += " "

    # loop through the innings, formatting on the fly
    for idx_lsi, lsi in enumerate(linescoreinning_list):
        # spaces_linescore_dense += 1 # border char before
        spaces_linescore_dense += 1  # buffer space before
        spaces_linescore_dense += max(
            lsi.get_appetite(), min_spaces_dense
        )  # spaces needed for this lsi element
        spaces_linescore_dense += 1  # buffer space after
        spaces_linescore_dense += 1  # border char after
        format_line_dense += (
            " %" + str(max(lsi.get_appetite(), min_spaces_dense)) + "s %1s"
        )
        substitution_set_line_top_dense.append(lsi.inn_no)
        substitution_set_line_away_dense.append(lsi.R_away)
        substitution_set_line_home_dense.append(
            lsi.R_home if lsi.R_home is not None else " " * lsi.get_appetite()
        )
        substitution_set_line_bot_dense.append(horz_char * lsi.get_appetite())
        substitution_set_line_top_dense.append(cross_char)
        substitution_set_line_away_dense.append(cross_char)
        substitution_set_line_home_dense.append(cross_char)
        substitution_set_line_bot_dense.append(cross_char)

        if (idx_lsi % 3 == 0) and (idx_lsi != 0):
            spaces_linescore_sparse += 2  # every three innings, add extra spaces before
            format_line_sparse += "  "
        spaces_linescore_sparse += max(
            lsi.get_appetite(), min_spaces_sparse
        )  # space needed for this lsi element
        spaces_linescore_sparse += 1  # buffer space after
        format_line_sparse += (
            "%" + str(max(lsi.get_appetite(), min_spaces_sparse)) + "s "
        )
        substitution_set_line_top_sparse.append(lsi.inn_no)
        substitution_set_line_away_sparse.append(lsi.R_away)
        substitution_set_line_home_sparse.append(
            lsi.R_home if lsi.R_home is not None else " " * lsi.get_appetite()
        )

    # work on RHE ending
    spaces_linescore_sparse += 2  # buffer spaces before summary
    format_line_sparse += " -"
    RHE_dict = extract_RHE(linescoreinning_list)  # get the RHE stuff
    for RHEcode in ["R", "H", "E"]:
        spaces_linescore_dense += 1  # buffer space before summary term
        spaces_linescore_dense += RHE_dict[RHEcode]["spaces"]
        spaces_linescore_dense += 1  # buffer space after summary term
        spaces_linescore_dense += 1  # border char after summary term
        format_line_dense += " %" + str(RHE_dict[RHEcode]["spaces"]) + "s %1s"
        substitution_set_line_top_dense.append(RHEcode)
        substitution_set_line_away_dense.append(RHE_dict[RHEcode]["away"])
        substitution_set_line_home_dense.append(RHE_dict[RHEcode]["home"])
        substitution_set_line_bot_dense.append(horz_char * RHE_dict[RHEcode]["spaces"])
        substitution_set_line_top_dense.append(cross_char)
        substitution_set_line_away_dense.append(cross_char)
        substitution_set_line_home_dense.append(cross_char)
        substitution_set_line_bot_dense.append(cross_char)

        spaces_linescore_sparse += 1  # buffer spaces before summary term
        spaces_linescore_sparse += RHE_dict[RHEcode]["spaces"]
        format_line_sparse += " %" + str(RHE_dict[RHEcode]["spaces"]) + "s"
        substitution_set_line_top_sparse.append(RHEcode)
        substitution_set_line_away_sparse.append(RHE_dict[RHEcode]["away"])
        substitution_set_line_home_sparse.append(RHE_dict[RHEcode]["home"])

    residual_spaces_dense = (_CLI_LINE_LENGTH_WIDE_DEFAULT if wide_display else _CLI_LINE_LENGTH_DEFAULT) - spaces_linescore_dense
    residual_spaces_sparse = (_CLI_LINE_LENGTH_WIDE_DEFAULT if wide_display else _CLI_LINE_LENGTH_DEFAULT) - spaces_linescore_sparse

    spaces_team_fullname = max([len(team.full_name) for team in teams.values()])
    spaces_team_cityname = max([len(team.location_name) for team in teams.values()])
    spaces_team_shortname = max([len(team.short_name) for team in teams.values()])

    def dtf(x_in):
        if force_uppercase_team:
            return x_in.upper()
        return x_in  # pass through

    if residual_spaces_dense > spaces_team_fullname:
        format_name_dense += (
            "%" + str(residual_spaces_dense) + "s"
        )  # fill remaining spaces
        substitution_set_name_top_dense.append(horz_char * residual_spaces_dense)
        substitution_set_name_away_dense.append(dtf(teams["away"].full_name))
        substitution_set_name_home_dense.append(dtf(teams["home"].full_name))
        substitution_set_name_bot_dense.append(horz_char * residual_spaces_dense)
    elif residual_spaces_dense > spaces_team_shortname:
        format_name_dense += (
            "%-" + str(residual_spaces_dense) + "s"
        )  # fill remaining spaces
        substitution_set_name_top_dense.append(horz_char * residual_spaces_dense)
        substitution_set_name_away_dense.append(dtf(teams["away"].short_name))
        substitution_set_name_home_dense.append(dtf(teams["home"].short_name))
        substitution_set_name_bot_dense.append(horz_char * residual_spaces_dense)
    elif residual_spaces_dense > spaces_team_cityname:
        format_name_dense += (
            "%-" + str(residual_spaces_dense) + "s"
        )  # fill remaining spaces
        substitution_set_name_top_dense.append(horz_char * residual_spaces_dense)
        substitution_set_name_away_dense.append(dtf(teams["away"].location_name))
        substitution_set_name_home_dense.append(dtf(teams["home"].location_name))
        substitution_set_name_bot_dense.append(horz_char * residual_spaces_dense)
    else:
        magic_number = max(3, residual_spaces_dense)
        format_name_dense += "%" + str(magic_number) + "s"
        substitution_set_name_top_dense.append(horz_char * magic_number)
        substitution_set_name_away_dense.append(teams["away"].abbrev)
        substitution_set_name_home_dense.append(teams["home"].abbrev)
        substitution_set_name_bot_dense.append(horz_char * magic_number)
    format_name_sparse += "%3s  "
    substitution_set_name_top_sparse.append(horz_char * 3)
    substitution_set_name_away_sparse.append(teams["away"].abbrev)
    substitution_set_name_home_sparse.append(teams["home"].abbrev)

    lines_dense = []
    lines_sparse = []

    # print the results (DEBUG!!!!!)
    lines_dense.append(
        (format_name_dense % tuple(substitution_set_name_top_dense))
        + (format_line_dense % tuple(substitution_set_line_top_dense))
    )
    if use_top_spacing_line:
        lines_dense.append(
            (format_name_dense % tuple(substitution_set_name_bot_dense))
            + (format_line_dense % tuple(substitution_set_line_bot_dense))
        )
    lines_dense.append(
        (format_name_dense % tuple(substitution_set_name_away_dense))
        + (format_line_dense % tuple(substitution_set_line_away_dense))
    )
    lines_dense.append(
        (format_name_dense % tuple(substitution_set_name_home_dense))
        + (format_line_dense % tuple(substitution_set_line_home_dense))
    )
    if use_bottom_spacing_line:
        lines_dense.append(
            (format_name_dense % tuple(substitution_set_name_bot_dense))
            + (format_line_dense % tuple(substitution_set_line_bot_dense))
        )

    lines_sparse.append(
        (format_name_sparse % tuple(substitution_set_name_away_sparse))
        + (format_line_sparse % tuple(substitution_set_line_away_sparse))
    )
    lines_sparse.append(
        (format_name_sparse % tuple(substitution_set_name_home_sparse))
        + (format_line_sparse % tuple(substitution_set_line_home_sparse))
    )

    if venue is not None:
        venue_line = " " * indent_dense
        venue_line += cross_char + " "
        venue = " " + venue + " "  # add leading and trailing space
        venue_line_ending = cross_char + horz_char * 3 + cross_char
        fill_horz_char_venue = (
            (_CLI_LINE_LENGTH_WIDE_DEFAULT if wide_display else _CLI_LINE_LENGTH_DEFAULT)
            - len(venue_line)
            - len(venue)
            - len(venue_line_ending)
            - 1
        )
        venue_line += (
            horz_char * fill_horz_char_venue
            + cross_char
            + dtf(venue)
            + venue_line_ending
        )
        lines_dense.append(venue_line)

    if decision_dict is not None:
        decision_line = " " * indent_dense
        decision_line += cross_char + horz_char * 3 + cross_char
        spacer = cross_char + horz_char + cross_char
        dec_list = []
        for key in ["WP", "LP", "SV"]:
            if decision_dict[key] is not None:
                dec_list.append("%s: " % key + decision_dict[key])
        for idx_dec, dec_val in enumerate(dec_list):
            decision_line += " " + dtf(dec_val) + " "
            if idx_dec + 1 < len(dec_list):
                decision_line += spacer
            else:
                decision_line += cross_char
        fill_horz_char_decision = (_CLI_LINE_LENGTH_WIDE_DEFAULT if wide_display else _CLI_LINE_LENGTH_DEFAULT) - len(decision_line) - 1
        decision_line += horz_char * fill_horz_char_decision + cross_char
        lines_dense.append(decision_line)

    return lines_dense, lines_sparse
