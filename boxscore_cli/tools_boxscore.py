
class BoxScorePitcher(object):
    """
    store one line with pitcher results from a linescore
    """

    _lastname_player: str
    _firstname_player: str
    _jersey_player: int
    _innings_pitched: str
    _hits: int
    _runs: int
    _runs_earned: int
    _bb: int
    _strikeouts: int
    _hr: int

    def __init__(
        self,
        lastname_player,
        firstname_player,
        jersey_player,
        innings_pitched,
        hits,
        runs,
        runs_earned,
        bb,
        strikeouts,
        hr,
    ):
        self._lastname_player = lastname_player
        self._firstname_player = firstname_player
        self._jersey_player = jersey_player
        self._innings_pitched = innings_pitched
        self._hits = hits
        self._runs = runs
        self._runs_earned = runs_earned
        self._bb = bb
        self._strikeouts = strikeouts
        self._hr = hr

    @staticmethod
    def get_header_stats():
        """get the headers for each stat"""
        header_list = ["IP", "H", "R", "ER", "BB", "K", "HR"]
        return header_list

    def get_appetite_stats(self, incl_header=True):
        """get the appetite for spaces of each stat"""
        stat_list = [
            self.innings_pitched,
            self.hits,
            self.runs,
            self.runs_earned,
            self.bb,
            self.strikeouts,
            self.hr,
        ]
        len_list = [len(str(x)) if x is not None else 0 for x in stat_list]
        if not incl_header:
            return len_list
        else:
            return [
                max([xx, len(yy)])
                for xx, yy in list(zip(len_list, self.get_header_stats()))
            ]

    @property
    def lastname_player(self):
        return self._lastname_player

    @property
    def firstname_player(self):
        return self._firstname_player

    @property
    def jersey_player(self):
        return self._jersey_player

    @property
    def innings_pitched(self):
        return self._innings_pitched

    @property
    def hits(self):
        return self._hits

    @property
    def runs(self):
        return self._runs

    @property
    def runs_earned(self):
        return self._runs_earned

    @property
    def bb(self):
        return self._bb

    @property
    def strikeouts(self):
        return self._strikeouts

    @property
    def hr(self):
        return self._hr


class BoxScoreBatter(object):
    """
    store one line with player results from a linescore
    """

    _lastname_player: str
    _firstname_player: str
    _pos: str
    _jersey_player: int
    _batting_order: str
    _ab: int
    _runs: int
    _hits: int
    _rbi: int
    _bb: int
    _so: int
    _po: int
    _asst: int

    def __init__(
        self,
        lastname_player,
        firstname_player,
        pos,
        jersey_player,
        batting_order,
        ab,
        runs,
        hits,
        rbi,
        bb,
        so,
        po,
        asst,
    ):
        self._lastname_player = lastname_player
        self._firstname_player = firstname_player
        self._pos = pos
        self._jersey_player = jersey_player
        self._batting_order = str(batting_order) if batting_order is not None else None
        self._ab = ab
        self._runs = runs
        self._hits = hits
        self._rbi = rbi
        self._bb = bb
        self._so = so
        self._po = po
        self._asst = asst

    def __str__(self):
        return "%s, %s. a.k.a. %s (#%s, %s): %s for %s with %s rbi" % (
            self.lastname_player,
            self.firstinitial_player,
            self.firstname_player,
            self.jersey_player,
            self.pos,
            self.hits,
            self.ab,
            self.rbi,
        )

    @staticmethod
    def get_header_stats():
        """get the headers for each stat"""
        header_list = ["AB", "R", "H", "RBI", "BB", "SO", "PO", "A"]
        return header_list

    def get_appetite_stats(self, incl_header=True):
        """get the appetite for spaces of each stat"""
        stat_list = [
            self.ab,
            self.runs,
            self.hits,
            self.rbi,
            self.bb,
            self.so,
            self.po,
            self.asst,
        ]
        len_list = [len(str(x)) if x is not None else 0 for x in stat_list]
        if not incl_header:
            return len_list
        else:
            return [
                max([xx, len(yy)])
                for xx, yy in list(zip(len_list, self.get_header_stats()))
            ]

    @property
    def lastname_player(self):
        return self._lastname_player

    @property
    def firstname_player(self):
        return self._firstname_player

    @property
    def pos(self):
        return self._pos

    @property
    def jersey_player(self):
        return self._jersey_player

    @property
    def batting_order(self):
        return self._batting_order

    @property
    def ab(self):
        return self._ab

    @property
    def runs(self):
        return self._runs

    @property
    def hits(self):
        return self._hits

    @property
    def rbi(self):
        return self._rbi

    @property
    def bb(self):
        return self._bb

    @property
    def so(self):
        return self._so

    @property
    def po(self):
        return self._po

    @property
    def asst(self):
        return self._asst

    @property
    def firstinitial_player(self):
        return self._firstname_player[0]

