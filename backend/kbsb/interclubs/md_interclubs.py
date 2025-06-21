# copyright Ruben Decrop 2012 - 2024
# copyright Chessdevil Consulting BVBA 2015 - 2022

# we are using pydantic models (and not dicts) to represent
# to represent business obejcts

from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from enum import StrEnum, auto
from typing import Literal
from reddevil.core.dbbase import DbBase


# old interclub data
ICROUNDS = {
    1: date.fromisoformat("2023-09-24"),
    2: date.fromisoformat("2023-10-15"),
    3: date.fromisoformat("2023-10-22"),
    4: date.fromisoformat("2023-11-19"),
    5: date.fromisoformat("2023-12-03"),
    6: date.fromisoformat("2024-01-28"),
    7: date.fromisoformat("2024-02-04"),
    8: date.fromisoformat("2024-02-18"),
    9: date.fromisoformat("2024-03-10"),
    10: date.fromisoformat("2024-03-24"),
    11: date.fromisoformat("2024-04-24"),
}

PLAYERSPERDIVISION = {
    1: 8,
    2: 8,
    3: 6,
    4: 4,
    5: 4,
}


class GAMERESULT(StrEnum):
    NOTPLAYED = ""
    NOTOVERRULED = "NOR"
    HOMEWIN = "1-0"
    DRAW = "½-½"
    VISITWIN = "0-1"
    FORFEIT_VISIT = "1-0 FF"
    FORFEIT_HOME = "0-1 FF"
    FORFEIT_BOTH = "0-0 FF"
    SPECIAL_5_0 = "½-0"
    SPECIAL_0_5 = "0-½"
    FORFEIT_TEAM = "Team FF"


class PlayerlistNature(StrEnum):
    ASSIGNED = auto()
    UNASSIGNED = auto()
    IMPORTED = auto()
    EXPORTED = auto()
    LOCKED = auto()
    # older
    REQUESTEDIN = auto()
    CONFIRMEDOUT = auto()


class PlayerPeriod(StrEnum):
    """
    The periuod the assignment of the play took place
    """

    SEPTEMBER = auto()
    NOVEMBER = auto()
    JANUARY = auto()
    UNKNOWN = auto()


# interclub club


class ICTeam(BaseModel):
    """
    a submodel representing a team
    """

    division: int
    titular: list[int] | None = Field(default_factory=list)
    idclub: int
    index: str | None = ""
    name: str  # includes numbercat like "KOSK 1"
    pairingnumber: int | None = 0
    teamforfeit: bool = False


class ICPlayer(BaseModel):
    """
    a submodel representing a Player on player list of a club
    """

    assignedrating: int
    average: float = 0
    fiderating: int | None = 0
    first_name: str
    idnumber: int
    idcluborig: int  # the club the player belongs to in membermgmt
    idclubvisit: int  # the club the player is playing if he plays elsewhere. a transfer
    last_name: str
    natrating: int | None = 0
    nature: PlayerlistNature
    period: PlayerPeriod | None = None
    titular: str | None = None


class ICPlayerUpdateItem(BaseModel):
    """
    a input validator for an update of a single Player in the playerlist
    """

    assignedrating: int
    fiderating: int | None = 0
    first_name: str
    idnumber: int
    idcluborig: int  # the club the player belongs to in signaletique
    idclubvisit: int  # the club the player is playing if he plays elsewhere
    last_name: str
    natrating: int | None = 0
    nature: PlayerlistNature
    period: PlayerPeriod | None = None
    titular: str | None = None


class ICPlayerUpdate(BaseModel):
    """
    a input validator for a list of Player updates
    """

    players: list[ICPlayerUpdateItem]


class ICPlayerValidationError(BaseModel):
    """
    an output model for listing validation errors in the playerlist
    """

    errortype: Literal["ELO", "TitularOrder", "TitularCount"]
    idclub: int
    message: str
    detail: Any


class ICClubDB(BaseModel):
    """
    a IC club as written in the database
    """

    name: str | None = ""
    id: str | None = None
    idclub: int
    teams: list[ICTeam] | None = Field(default_factory=list)
    players: list[ICPlayer] | None = Field(default_factory=list)
    registered: bool | None = False


class ICClubItem(BaseModel):
    """
    an IC Club as part of a list of IC clubs
    """

    name: str
    idclub: int
    teams: list[ICTeam]
    registered: bool


# series


class ICGame(BaseModel):
    """
    a submodel representing a single game in the ICEncounter
    """

    idnumber_home: int | None = None
    idnumber_visit: int | None = None
    result: GAMERESULT = GAMERESULT.NOTPLAYED
    overruled: GAMERESULT | None = GAMERESULT.NOTOVERRULED

    model_config = ConfigDict(use_enum_values=True)


class ICGameDetails(BaseModel):
    """
    an output validator for the details of a IC Game
    """

    fullname_home: str
    fullname_visit: str
    idnumber_home: int
    idnumber_visit: int
    rating_home: int
    rating_visit: int
    result: GAMERESULT = GAMERESULT.NOTPLAYED
    overruled: GAMERESULT | None = GAMERESULT.NOTOVERRULED

    model_config = ConfigDict(use_enum_values=True)


class ICEncounter(BaseModel):
    """
    a submodel of ICSeries, representing an IC encounter between 2 teams
    """

    icclub_home: int
    icclub_visit: int
    pairingnr_home: int
    pairingnr_visit: int
    matchpoint_home: int = 0
    matchpoint_visit: int = 0
    boardpoint2_home: int = 0
    boardpoint2_visit: int = 0
    games: list[ICGame] = []
    played: bool = False
    signhome_idnumber: int = 0
    signhome_ts: datetime | None = None
    signvisit_idnumber: int = 0
    signvisit_ts: datetime | None = None


class ICRound(BaseModel):
    """
    a submodel in ICSeries, representing a single round
    """

    round: int
    rdate: str
    encounters: list[ICEncounter]


class ICSeriesDB(BaseModel):
    """
    an IC series as written to the database
    """

    division: int
    index: str = ""
    id: str
    teams: list[ICTeam] = []
    rounds: list[ICRound] = []


class ICSeries(BaseModel):
    """
    an internal model, representation of a single IC series
    """

    division: int
    index: str
    teams: list[ICTeam]
    rounds: list[ICRound] = []


class ICSeriesUpdate(BaseModel):
    """
    an internal model, representation of a single IC series
    """

    teams: list[ICTeam] | None = None
    rounds: list[ICRound] | None = None


class ICTeamGame(BaseModel):
    """
    an internal model, representing a result of a team in a round
    """

    boardpoints2: int = 0  # double boardpoints team won against opponent
    matchpoints: int = 0  # matchpoints team won against opponent
    pairingnumber_opp: int
    round: int


class ICTeamStanding(BaseModel):
    """
    a submodel of ICStandings, representing the standings a single team
    """

    name: str
    idclub: int
    pairingnumber: int
    matchpoints: int
    boardpoints: float
    games: list[ICTeamGame]


class ICStandingsDB(BaseModel):
    """
    the IC standings as written to the database
    """

    dirtytime: datetime | None = None
    division: int
    id: str | None = None
    index: str
    teams: list[ICTeamStanding]


class ICPlanningItem(BaseModel):
    """
    a submodel of ICPlanning, represnting the planning a single team of a club
    """

    division: int
    games: list[ICGame]
    idclub: int
    idclub_opponent: int
    index: str
    name: str
    name_opponent: str
    nrgames: int
    pairingnumber: int
    playinghome: bool
    round: int


class ICPlanning(BaseModel):
    """
    a input validator for the planning of IC club for a round
    """

    plannings: list[ICPlanningItem]


class ICResultItem(BaseModel):
    """
    a submodel for the incoming results of a single team in a club
    """

    boardpoints: str | None = None
    division: int
    games: list[ICGame]
    icclub_home: int
    icclub_visit: int
    index: str
    name_home: str
    name_visit: str
    nrgames: int
    matchpoints: str | None = None
    round: int
    pairingnr_home: int
    pairingnr_visit: int
    signhome_idnumber: int | None = 0
    signhome_ts: datetime | None = None
    signvisit_idnumber: int | None = 0
    signvisit_ts: datetime | None = None


class ICResult(BaseModel):
    """
    an input validator for a the incoming IC results of a club
    """

    results: list[ICResultItem]


# registration


class ICRegistrationDB(BaseModel):
    """
    an IC Registration as written in the database
    for doc purposes only
    """

    id: str
    idclub: int
    idinvoice: str
    idpaymentrequest: str
    locale: str
    name: str
    teams1: int
    teams2: int
    teams3: int
    teams4: int
    teams5: int
    wishes: dict[str, Any]


class ICRegistration(BaseModel):
    """
    an IC Registration as used internally
    """

    id: str | None = None
    idclub: int | None = None
    idinvoice: str | None = None
    idpaymentrequest: str | None = None
    locale: str | None = None
    name: str | None = None
    teams1: int | None = None
    teams2: int | None = None
    teams3: int | None = None
    teams4: int | None = None
    teams5: int | None = None
    wishes: dict | None = None


class ICRegistrationOut(BaseModel):
    """
    an IC Registration as used internally
    """

    id: str
    idclub: int
    idinvoice: str = ""
    idpaymentrequest: str = ""
    locale: str
    name: str
    teams1: int = 0
    teams2: int = 0
    teams3: int = 0
    teams4: int = 0
    teams5: int = 0
    wishes: dict = {}


class ICRegistrationHistory(BaseModel):
    """
    a model represnting the history of enrollments
    """

    action: str
    label: str
    idclub: str
    time: datetime


class ICRegistrationIn(BaseModel):
    """
    a input validator for an new enrollment
    """

    locale: str | None = "nl"
    idclub: int | None = None
    teams1: int
    teams2: int
    teams3: int
    teams4: int
    teams5: int
    wishes: dict
    name: str


# venues


class ICVenueItem(BaseModel):
    """
    a submodel representing a single Venue
    """

    address: str
    capacity: int  # number of boards, 0  is unlimited
    email: str | None = ""
    phone: str | None = ""
    remarks: str | None = ""
    rounds: list[str] | None = None
    teams: list[str] | None = None
    wheelchair: bool | None = False


class ICVenueIn(BaseModel):
    """
    an input validator for the IC Venues
    """

    venues: list[ICVenueItem]


class ICVenueDB(BaseModel):
    """
    all the IC venues for a club as written in the database
    """

    id: str | None = None
    idclub: int | None = None
    venues: list[ICVenueItem]


# DB classes


class DbICSeries(DbBase):
    COLLECTION = "ic_series"
    DOCUMENTTYPE = ICSeriesDB
    VERSION = 1
    IDGENERATOR = "uuid"


class DbICSeries2324(DbBase):
    COLLECTION = "interclub2324series"
    DOCUMENTTYPE = ICSeriesDB
    VERSION = 1
    IDGENERATOR = "uuid"


class DbICSeries2425(DbBase):
    COLLECTION = "interclub2425series"
    DOCUMENTTYPE = ICSeriesDB
    VERSION = 1
    IDGENERATOR = "uuid"


class DbICStandings(DbBase):
    COLLECTION = "ic_standings"
    DOCUMENTTYPE = ICStandingsDB
    VERSION = 1
    IDGENERATOR = "uuid"


class DbICStandings2324(DbBase):
    COLLECTION = "ic_2324_standings"
    DOCUMENTTYPE = ICStandingsDB
    VERSION = 1
    IDGENERATOR = "uuid"


class DbICStandings2425(DbBase):
    COLLECTION = "ic_2425_standings"
    DOCUMENTTYPE = ICStandingsDB
    VERSION = 1
    IDGENERATOR = "uuid"


class DbICVenue(DbBase):
    COLLECTION = "ic_venues"
    DOCUMENTTYPE = ICVenueDB
    VERSION = 1
    IDGENERATOR = "uuid"
    HISTORY = True


class DbICClub(DbBase):
    COLLECTION = "ic_club"
    DOCUMENTTYPE = ICClubDB
    VERSION = 1
    IDGENERATOR = "uuid"
    HISTORY = True


class DbICRegistration(DbBase):
    COLLECTION = "ic_registration"
    DOCUMENTTYPE = ICRegistrationDB
    VERSION = 1
    IDGENERATOR = "uuid"
    HISTORY = True
