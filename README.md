# boxscore-cli

A CLI boxscore generator.

The newspaper boxscore was basically a perfect way to aggregate data about a given day's games.

Nowadays, nobody reads physical papers anymore, but nerds still use command line interfaces; if there was ever a second-best place for a boxscore, it was a CLI.

## CLI Design

The traditional CLI is 80 characters, which leaves 78 between outside bars:
```
+------------------------------------------------------------------------------+
0---------1---------2---------3---------4---------5---------6---------7--------|
01234567890123456789012345678901234567890123456789012345678901234567890123456789   <- zero indexed
0---------1---------2---------3---------4---------5---------6---------7--------8
12345678901234567890123456789012345678901234567890123456789012345678901234567890   <- one indexed
+------------------------------------------------------------------------------+
|                                                                              |
+--------------------------------------++--------------------------------------+
|                                      ||                                      |
+--------------------------------------++--------------------------------------+
```
If we want to evenly split the section (as above), there are 4 bars, leaving 76/2=38 spaces per column.
This will be common in a boxscore.

## Boxscore design

### Linescore

The top of a boxscore is the line score, giving the two-line summary of the teams run totals per inning plus totals of runs, hits, and errors:
```
+------------------------------------------------------------------------------+
+------------------+  1 +  2 +  3 +  4 +  5 +  6 +  7 +  8 +  9 +  R +  H +  E +
| SAN DIEGO        +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +
| BALTIMORE        +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +
+-------------------------------------------+ ORIOLE PARK AT CAMDEN YARDS +----+
+---+ WP: JONES +---+ LP: SMITH +---+ SV: JOHNSON +----------------------------+
```
The linescore postscript includes the winning pitcher and the losing pitcher, as well as the pitcher that accumulated a save; I also like when it features the name of the ballpark.
Use of 2 digits + 2 padding digits should guarantee realistic scores fit on a per-inning basis.
In the event that a game goes to (moderate) extra innings, team names should be compacted to the 3-letter codes:
```
+------------------------------------------------------------------------------+
+--------+  1 +  2 +  3 +  4 +  5 +  6 +  7 +  8 +  9 + 10 + 11 +  R +  H +  E +
+ SD     +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +
+ BAL    +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +
+-------------------------------------------+ ORIOLE PARK AT CAMDEN YARDS +----+
+---+ WP: JONES +---+ LP: SMITH +---+ SV: JOHNSON +----------------------------+
```
This gets us to 11 innings.

An alternate, more compact rendering of the linescore could be given as follows:
```
+------------------------------------------------------------------------------+
+ San Diego      0 0 0   0 0 0   0 0 0   0 0 0   0 0 0   0 0 0   0 0 0 - 0 0 0 +
+ Baltimore      0 0 0   0 0 0   0 0 0   0 0 0   0 0 0   0 0 0   0 0 1 - 1 1 0 +
+------------------------------------------------------------------------------+
```
This renders 18 innings, and it can be truncated further to render 24:
```
+------------------------------------------------------------------------------+
+ SD     0 0 0   0 0 0   0 0 0   0 0 0   0 0 0   0 0 0   0 0 0   0 0 0 - 0 0 0 +
+ BAL    0 0 0   0 0 0   0 0 0   0 0 0   0 0 0   0 0 0   0 0 1   0 0 0 - 1 1 0 +
+------------------------------------------------------------------------------+
```
Ideally, we intelligently balance completeness and aesthetically ideal display; it's worth noting that we still don't have space [for the 33-inning, 8.5 hour 1981 game between the Pawtucket Red Sox and the Rochester Red Wings](https://en.wikipedia.org/wiki/Longest_professional_baseball_game), nor the [26-inning longest game in MLB history](https://www.mlb.com/news/longest-games-in-baseball-history-c275773542), although only three MLB games have gone that distance.
If something like that happens, a split box score (or just an error message) will probably suffice.

### Boxscore proper

Boxscores typically consist of a compact review of the game: date, location, and linescore:
```
+ Sunday, 01 January 1921                                                      + <- metadata
+ Orioles Park and Camden Yards                                                +
+                                                                              + <- linescore
+   San Diego      0 0 0   0 0 0   0 0 0 - 0 0 0                               +
+   Baltimore      0 0 0   0 0 0   0 0 0 - 1 1 0                               +
+                                                                              +
+ SAN DIEGO PADRES                                                             + <- away team
+                                      + AB +  R +  H + RBI+ BB + SO + PO +  A + <- batting stats
+   McCringleberry, H. CF              +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +
+   Chonk, D. 2B                       +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +
+     Diesel, S. PH                    +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +
+     James, L. 3B                     +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +
+   Laser, M. 1B                       +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +
+   ...                                                                        +
+                                                                              +
+                                    +   IP +  H +  R + ER + BB + SO + HR + BFP+ <- pitching stats
+   Christmas, L.                    +  0.0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +
+   ...                                                                        +
+                                                                              +
+   FIELDING                                                                   +
+     DP: 1. Laser-James-Chonk                                                 +
+     E: James (4)                                                             +
+   BATTING                                                                    +
+     HR: Chonk                                                                +
+     HBP: Chonk                                                               +
+   BASERUNNING                                                                +
+     SB: Laser                                                                +
+                                                                              +
+ BALTIMORE ORIOLES                                                            + <- home team
+                                      + AB +  R +  H + RBI+ BB + SO + PO +  A + <- batting stats
+   Roberts, B. 2B                     +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +
+   Ripken Jr., C. SS                  +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +
+   Jones, A. CF                       +  0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +
+   ...                                                                        +
+                                                                              +
+                                    +   IP +  H +  R + ER + BB + SO + HR + BFP+ <- pitching stats
+  Means, J    .                     +  0.0 +  0 +  0 +  0 +  0 +  0 +  0 +  0 +
+  ...                                                                         +
+                                                                              +
+   FIELDING                                                                   +
+     E: Roberts (4)                                                           +
+   BATTING                                                                    +
+     HR: Jones                                                                +
+     HBP: Ripken Jr                                                           +
+   BASERUNNING                                                                +
+     CS: Roberts                                                              +
+                                                                              +
```

The selection of stats here mirrors the [Wikipedia definition of a baseball box score](https://en.wikipedia.org/wiki/Box_score_(baseball).
Good examples of box scores have different stuff, like [the Athletic's swaggy minimal boxscores](https://theathletic.com/mlb/game/stats/baltimore-orioles-vs-texas-rangers/hMFZtTS71GJ6jQy3/) or [Baseball-Reference's incomprehensibly technical ones](https://www.baseball-reference.com/boxes/TEX/TEX202304030.shtml).

Final determination of the stats for this CLI program are yet to come.
