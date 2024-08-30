class LineScoreInning(object):
    """
    store a linescore inning
    """

    _inn_no: int
    _R_away: int
    _H_away: int
    _E_away: int
    _LOB_away: int
    _R_home: int
    _H_home: int
    _E_home: int
    _LOB_home: int
    _ordinal: str

    @property
    def inn_no(self):
        return self._inn_no

    @inn_no.setter
    def inn_no(self, value):
        self._inn_no = value

    @property
    def ordinal(self):
        return self._ordinal

    @ordinal.setter
    def ordinal(self, value):
        self._ordinal = value

    @property
    def R_away(self):
        return self._R_away

    @R_away.setter
    def R_away(self, value):
        self._R_away = value

    @property
    def H_away(self):
        return self._H_away

    @H_away.setter
    def H_away(self, value):
        self._H_away = value

    @property
    def E_away(self):
        return self._E_away

    @E_away.setter
    def E_away(self, value):
        self._E_away = value

    @property
    def LOB_away(self):
        return self._LOB_away

    @LOB_away.setter
    def LOB_away(self, value):
        self._LOB_away = value

    @property
    def R_home(self):
        return self._R_home

    @R_home.setter
    def R_home(self, value):
        self._R_home = value

    @property
    def H_home(self):
        return self._H_home

    @H_home.setter
    def H_home(self, value):
        self._H_home = value

    @property
    def E_home(self):
        return self._E_home

    @E_home.setter
    def E_home(self, value):
        self._E_home = value

    @property
    def LOB_home(self):
        return self._LOB_home

    @LOB_home.setter
    def LOB_home(self, value):
        self._LOB_home = value

    def __init__(self, inn_no: int, away=[0, 0, 0, 0], home=[0, 0, 0, 0]):
        """
        create an inning object
        """

        self._inn_no = inn_no
        self.R_away = away[0]
        self.H_away = away[1]
        self.E_away = away[2]
        self.LOB_away = away[3] if len(away) > 3 else None
        self.R_home = home[0]
        self.H_home = home[1]
        self.E_home = home[2]
        self.LOB_home = home[3] if len(home) > 3 else None

    def get_appetite(self) -> int:
        """
        figure out how many characters this inning needs to print
        """

        vars = [
            self._inn_no,
            self._R_away,
            self._H_away,
            self._E_away,
            self._LOB_away,
            self._R_home,
            self._H_home,
            self._E_home,
            self._LOB_home,
        ]

        # return the longest length of the converted string
        return max([len(str(var)) for var in vars if var is not None])


def extract_RHE(linescoreinning_list: list[LineScoreInning]):
    R_away = 0
    R_home = 0
    H_away = 0
    H_home = 0
    E_away = 0
    E_home = 0
    LOB_away = 0
    LOB_home = 0

    for lsi in linescoreinning_list:
        R_away += lsi.R_away if lsi.R_away is not None else 0
        R_home += lsi.R_home if lsi.R_home is not None else 0
        H_away += lsi.H_away if lsi.H_away is not None else 0
        H_home += lsi.H_home if lsi.H_home is not None else 0
        E_away += lsi.E_away if lsi.E_away is not None else 0
        E_home += lsi.E_home if lsi.E_home is not None else 0
        LOB_away += lsi.LOB_away if lsi.LOB_away is not None else 0
        LOB_home += lsi.LOB_home if lsi.LOB_home is not None else 0

    RHE_dict = {}
    RHE_dict["R"] = {
        "spaces": max([len(str(x)) for x in [R_away, R_home]]),
        "away": R_away,
        "home": R_home,
    }
    RHE_dict["H"] = {
        "spaces": max([len(str(x)) for x in [H_away, H_home]]),
        "away": H_away,
        "home": H_home,
    }
    RHE_dict["E"] = {
        "spaces": max([len(str(x)) for x in [E_away, E_home]]),
        "away": E_away,
        "home": E_home,
    }
    RHE_dict["LOB"] = {
        "spaces": max([len(str(x)) for x in [LOB_away, LOB_home]]),
        "away": LOB_away,
        "home": LOB_home,
    }

    return RHE_dict
