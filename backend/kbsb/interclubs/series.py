# copyright Ruben Decrop 2012 - 2024

import logging
from typing import cast, Any
from datetime import datetime, timezone, timedelta, time
from reddevil.core import (
    RdBadRequest,
    RdNotFound,
    get_settings,
    get_mongodb,
    encode_model,
)
from . import (
    GAMERESULT,
    # ICROUNDS,
    ICEncounter,
    ICGame,
    ICGameDetails,
    ICPlanningItem,
    ICResultItem,
    ICRound,
    ICSeries,
    ICSeriesDB,
    ICSeriesUpdate,
    ICStandingsDB,
    ICTeam,
    ICTeamGame,
    ICTeamStanding,
    DbICSeries,
    DbICSeries2324,
    DbICStandings,
    DbICStandings2324,
    anon_getICclub,
    load_icdata,
    ptable,
)

logger = logging.getLogger(__name__)

settings = get_settings()


# CRUD


async def create_icseries(division: str, index: str | None) -> str:
    """
    create a new InterclubSeries returning its id
    """
    logger.debug("create icseries")
    doc = {"division": division, "index": index or "", "teams": []}
    logger.debug("create series {doc}")
    return await DbICSeries.add(doc)


async def get_icseries(id: str, options: dict | None = None) -> ICSeries:
    """
    get the interclub series
    """
    logger.debug("get icseries")
    filter = dict(options or {})
    filter["_model"] = filter.pop("_model", ICSeries)
    filter["id"] = id
    return cast(ICSeries, await DbICSeries.find_single(filter))


async def get_icseries2(options: dict | None = None) -> list[ICSeries]:
    """
    get the interclub series
    """
    logger.debug("get icseries2")
    filter = dict(options or {})
    filter["_model"] = filter.pop("_model", ICSeries)
    return [cast(ICSeries, x) for x in await DbICSeries.find_multiple(filter)]


async def get_icseries_all() -> list[ICSeries]:
    """
    get all the interclub series
    """
    return [
        cast(ICSeries, x) for x in await DbICSeries.find_multiple({"_model": ICSeries})
    ]


async def update_icseries(
    division: int, index: str, iu: ICSeriesUpdate, options: dict[str, Any] | None = None
) -> ICSeries:
    """
    update a interclub series
    """
    logger.info(f"update icseries {division} {index}")
    options1 = dict(options or {})
    options1["_model"] = options1.pop("_model", ICSeries)
    iudict = iu.model_dump(exclude_unset=True)
    return cast(
        ICSeries,
        await DbICSeries.update(
            {"division": division, "index": index}, iudict, options1
        ),
    )


# business methods


async def isRoundOpen(round: int):
    """
    returns True is we passed 15h of the day of the round
    """
    icdata = await load_icdata()
    rounddate = icdata["rounds"].get(round)
    if not rounddate:
        return False
    rounddatetime = datetime.combine(rounddate, time(15))
    return datetime.now() > rounddatetime


async def anon_get_icseries_clubround(idclub: int, round: int) -> list[ICSeries]:
    """
    get IC club by idclub, returns None if nothing found or round is not open yet
    """
    if not await isRoundOpen(round):
        return []
    db = get_mongodb()
    coll = db[DbICSeries.COLLECTION]
    proj = {i: 1 for i in ICSeries.model_fields.keys()}
    if round:
        proj["rounds"] = {"$elemMatch": {"round": round}}
    filter = {}
    if idclub:
        filter["teams.idclub"] = idclub
    series = []
    async for doc in coll.find(filter, proj):
        s = encode_model(doc, ICSeries)
        series.append(s)
    return series


async def clb_getICseries(idclub: int, round: int) -> list[ICSeries] | None:
    """
    get IC club by idclub, returns None if nothing found
    """
    db = get_mongodb()
    coll = db[DbICSeries.COLLECTION]
    proj = {i: 1 for i in ICSeries.model_fields.keys()}
    if round:
        proj["rounds"] = {"$elemMatch": {"round": round}}
    filter = {}
    if idclub:
        filter["teams.idclub"] = idclub
    series = []
    cursor = coll.find(filter, proj)
    for doc in await cursor.to_list(length=100):
        series.append(encode_model(doc, ICSeries))
    return series


async def clb_saveICplanning(plannings: list[ICPlanningItem]) -> None:
    """
    save a lists of pleanning per team
    """
    for plan in plannings:
        s = await DbICSeries.find_single(
            {"division": plan.division, "index": plan.index, "_model": ICSeries}
        )
        curround = None
        for r in s.rounds:
            if r.round == plan.round:
                curround = r
        if not curround:
            raise RdBadRequest(description="InvalidRound")
        for enc in curround.encounters:
            if (
                plan.playinghome
                and (enc.icclub_home == plan.idclub)
                and (plan.pairingnumber == enc.pairingnr_home)
            ):
                if enc.games:
                    for ix, g in enumerate(enc.games):
                        g.idnumber_home = plan.games[ix].idnumber_home or 0
                else:
                    enc.games = [
                        ICGame(
                            idnumber_home=g.idnumber_home or 0,
                            idnumber_visit=0,
                        )
                        for g in plan.games
                    ]
            if (
                not plan.playinghome
                and (enc.icclub_visit == plan.idclub)
                and (plan.pairingnumber == enc.pairingnr_visit)
            ):
                if enc.games:
                    for ix, g in enumerate(enc.games):
                        g.idnumber_visit = plan.games[ix].idnumber_visit or 0
                else:
                    enc.games = [
                        ICGame(
                            idnumber_home=0,
                            idnumber_visit=g.idnumber_visit or 0,
                        )
                        for g in plan.games
                    ]
        await DbICSeries.update(
            {"division": plan.division, "index": plan.index},
            {"rounds": [r.model_dump() for r in s.rounds]},
        )


async def mgmt_saveICresults(results: list[ICResultItem]) -> None:
    """
    save a list of results per team
    """
    for res in results:
        s = await DbICSeries.find_single(
            {"division": res.division, "index": res.index, "_model": ICSeries}
        )
        curround = None
        for r in s.rounds:
            if r.round == res.round:
                curround = r
        if not curround:
            raise RdBadRequest(description="InvalidRound")
        for enc in curround.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            if (
                enc.icclub_home == res.icclub_home
                and enc.icclub_visit == res.icclub_visit
                and enc.pairingnr_home == res.pairingnr_home
                and enc.pairingnr_visit == res.pairingnr_visit
            ):
                enc.games = [
                    ICGame(
                        idnumber_home=g.idnumber_home,
                        idnumber_visit=g.idnumber_visit,
                        result=g.result,
                        overruled=g.overruled,
                    )
                    for g in res.games
                ]
                if res.signhome_idnumber:
                    enc.signhome_idnumber = res.signhome_idnumber
                    enc.signhome_ts = res.signhome_ts
                if res.signvisit_idnumber:
                    enc.signvisit_idnumber = res.signvisit_idnumber
                    enc.signvisit_ts = res.signvisit_ts
                calc_points(enc)
        await DbICSeries.update(
            {"division": res.division, "index": res.index},
            {"rounds": [r.model_dump() for r in s.rounds]},
        )
        await calc_standings(s)


async def clb_saveICresults(results: list[ICResultItem]) -> None:
    """
    save a list of results per team
    """
    # TODO check for time
    for res in results:
        s = await DbICSeries.find_single(
            {"division": res.division, "index": res.index, "_model": ICSeries}
        )
        curround = None
        for r in s.rounds:
            if r.round == res.round:
                curround = r
        if not curround:
            raise RdBadRequest(description="InvalidRound")
        for enc in curround.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            if (
                enc.icclub_home == res.icclub_home
                and enc.icclub_visit == res.icclub_visit
            ):
                enc.games = [
                    ICGame(
                        idnumber_home=g.idnumber_home,
                        idnumber_visit=g.idnumber_visit,
                        result=g.result,
                    )
                    for g in res.games
                ]
                if res.signhome_idnumber:
                    enc.signhome_idnumber = res.signhome_idnumber
                    enc.signhome_ts = res.signhome_ts
                if res.signvisit_idnumber:
                    enc.signvisit_idnumber = res.signvisit_idnumber
                    enc.signvisit_ts = res.signvisit_ts
                calc_points(enc)
        await DbICSeries.update(
            {"division": res.division, "index": res.index},
            {"rounds": [r.model_dump() for r in s.rounds]},
        )
        await calc_standings(s)


def calc_points(enc: ICEncounter):
    """
    calculate the matchpoint and boardpoint for the encounter
    """
    enc.boardpoint2_home = 0
    enc.boardpoint2_visit = 0
    enc.matchpoint_home = 0
    enc.matchpoint_visit = 0
    allfilled = True
    forfeited = False
    for g in enc.games:
        result = (
            g.overruled
            if g.overruled and g.overruled != GAMERESULT.NOTOVERRULED
            else g.result
        )
        if result in [GAMERESULT.HOMEWIN, GAMERESULT.FORFEIT_VISIT]:
            enc.boardpoint2_home += 2
        if result in [GAMERESULT.VISITWIN, GAMERESULT.FORFEIT_HOME]:
            enc.boardpoint2_visit += 2
        if result in [GAMERESULT.DRAW, GAMERESULT.SPECIAL_5_0]:
            enc.boardpoint2_home += 1
        if result in [GAMERESULT.DRAW, GAMERESULT.SPECIAL_0_5]:
            enc.boardpoint2_visit += 1
        if result == GAMERESULT.FORFEIT_TEAM:
            forfeited = True
        if result == GAMERESULT.NOTPLAYED:
            allfilled = False
    if allfilled:
        enc.played = True
        if not forfeited:
            if enc.boardpoint2_home > enc.boardpoint2_visit:
                enc.matchpoint_home = 2
            if enc.boardpoint2_home == enc.boardpoint2_visit:
                enc.matchpoint_home = 1
                enc.matchpoint_visit = 1
            if enc.boardpoint2_home < enc.boardpoint2_visit:
                enc.matchpoint_visit = 2


async def anon_getICencounterdetails(
    division: int,
    index: str,
    round: int,
    icclub_home: int,
    icclub_visit: int,
    pairingnr_home: int,
    pairingnr_visit: int,
) -> list[ICGameDetails]:
    if not await isRoundOpen(round):
        return []
    icserie = await DbICSeries.find_single(
        {
            "_model": ICSeries,
            "division": division,
            "index": index,
        }
    )
    details = []
    for r in icserie.rounds:
        if r.round == round:
            for enc in r.encounters:
                if not enc.icclub_home or not enc.icclub_visit:
                    continue
                if (
                    enc.icclub_home == icclub_home
                    and enc.icclub_visit == icclub_visit
                    and enc.pairingnr_home == pairingnr_home
                    and enc.pairingnr_visit == pairingnr_visit
                ):
                    homeclub = await anon_getICclub(icclub_home)
                    homeplayers = {p.idnumber: p for p in homeclub.players}
                    visitclub = await anon_getICclub(icclub_visit)
                    visitplayers = {p.idnumber: p for p in visitclub.players}
                    for g in enc.games:
                        if not g.idnumber_home or not g.idnumber_visit:
                            continue
                        hpl = homeplayers[g.idnumber_home]
                        vpl = visitplayers[g.idnumber_visit]
                        details.append(
                            ICGameDetails(
                                idnumber_home=g.idnumber_home,
                                fullname_home=f"{hpl.last_name}, {hpl.first_name}",
                                rating_home=hpl.assignedrating,
                                idnumber_visit=g.idnumber_visit,
                                fullname_visit=f"{vpl.last_name}, {vpl.first_name}",
                                rating_visit=vpl.assignedrating,
                                result=g.result,
                                overruled=g.overruled,
                            )
                        )
    return details


async def calc_standings(series: ICSeries) -> ICStandingsDB:
    """
    calculates and persists standings of a series
    """
    logger.info(f"recalculate standings {series.division}{series.index}")
    try:
        standings = await DbICStandings.find_single(
            {
                "division": series.division,
                "index": series.index,
                "_model": ICStandingsDB,
            }
        )
    except RdNotFound:
        standings = ICStandingsDB(
            division=series.division,
            index=series.index,
            teams=[
                ICTeamStanding(
                    name=t.name,
                    idclub=t.idclub,
                    pairingnumber=t.pairingnumber,
                    matchpoints=0,
                    boardpoints=0,
                    games=[],
                )
                for t in series.teams
                if t.idclub
            ],
        )
        await DbICStandings.add(standings.model_dump(exclude_none=True))
    for r in series.rounds:
        for enc in r.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            if not enc.played:
                continue
            team_home = next(
                (x for x in standings.teams if x.pairingnumber == enc.pairingnr_home),
                None,
            )
            team_visit = next(
                (x for x in standings.teams if x.pairingnumber == enc.pairingnr_visit),
                None,
            )
            game_home = next(
                (
                    x
                    for x in team_home.games
                    if x.pairingnumber_opp == team_visit.pairingnumber
                ),
                None,
            )
            if not game_home:
                game_home = ICTeamGame(
                    pairingnumber_opp=team_visit.pairingnumber, round=r.round
                )
                team_home.games.append(game_home)
            game_visit = next(
                (
                    x
                    for x in team_visit.games
                    if x.pairingnumber_opp == team_home.pairingnumber
                ),
                None,
            )
            if not game_visit:
                game_visit = ICTeamGame(
                    pairingnumber_opp=team_home.pairingnumber, round=r.round
                )
                team_visit.games.append(game_visit)
            game_home.matchpoints = enc.matchpoint_home
            game_home.boardpoints2 = enc.boardpoint2_home
            game_visit.matchpoints = enc.matchpoint_visit
            game_visit.boardpoints2 = enc.boardpoint2_visit
    for t in standings.teams:
        t.matchpoints = sum(g.matchpoints for g in t.games)
        t.boardpoints = sum(g.boardpoints2 for g in t.games) / 2
    standings.teams = sorted(
        standings.teams, key=lambda t: (-t.matchpoints, -t.boardpoints)
    )
    standings.dirtytime = None
    return await DbICStandings.update(
        {
            "division": series.division,
            "index": series.index,
        },
        standings.model_dump(),
        {"_model": ICStandingsDB},
    )


async def anon_getICstandings(idclub: int) -> list[ICStandingsDB] | None:
    """
    get the Standings by club
    """
    options = {"_model": ICStandingsDB}
    if idclub:
        options["teams.idclub"] = idclub
    docs = await DbICStandings.find_multiple(options)
    for ix, d in enumerate(docs):
        dirty = d.dirtytime.replace(tzinfo=timezone.utc) if d.dirtytime else None
        if dirty and dirty < datetime.now(timezone.utc) - timedelta(minutes=5):
            logger.info("recalc standings")
            series = await DbICSeries.find_single(
                {"division": d.division, "index": d.index, "_model": ICSeries}
            )
            docs[ix] = await calc_standings(series)
    return docs


dbseasons = {
    "2324": DbICStandings2324,
    "2425": DbICStandings2425,
}
dbseries = {
    "2324": DbICSeries2324,
    "2425": DbICSeries2425,
}


async def anon_getICstandingsArchive(season: str) -> list[ICStandingsDB] | None:
    """
    get the Standings by club
    """
    options = {"_model": ICStandingsDB}
    dbseason = dbseasons[season]
    return await dbseason.find_multiple(options)


async def anon_getICresultsArchive(season: str, round: int) -> list[ICSeriesDB]:
    """
    get IC results from a season for a round
    """
    dbresult = dbseries[season]
    db = get_mongodb()
    coll = db[dbresult.COLLECTION]
    logger.info(f"coll {coll}")
    proj = {i: 1 for i in ICSeries.model_fields.keys()}
    proj["rounds"] = {"$elemMatch": {"round": round}}
    logger.info(f"proj {proj}")
    series = []
    async for doc in coll.find({}, proj):
        try:
            doc["id"] = str(doc["_id"])
            s = encode_model(doc, ICSeriesDB)
        except Exception as e:
            logger.error(f"encoding ICSeriesDB {doc}")
            continue
        series.append(s)
    return series


async def mgmt_register_teamforfeit(division: int, index: str, name: str) -> None:
    """
    register a team default
    don't do this for the last round or the standings won't be correct
    """
    logger.info("teamforfeit")
    series = cast(
        ICSeries,
        await DbICSeries.find_single(
            {
                "division": division,
                "index": index,
                "_model": ICSeriesDB,
            }
        ),
    )
    logger.info(f"found series {series.division} {series.index}")
    for t in series.teams:
        if t.name == name:
            team = t
            break
    else:
        raise RdNotFound(description="TeamNotFound")
    team.teamforfeit = True
    for r in series.rounds:
        for enc in r.encounters:
            if team.pairingnumber in [enc.pairingnr_home, enc.pairingnr_visit]:
                if enc.games:
                    for g in enc.games:
                        g.overruled = GAMERESULT.FORFEIT_TEAM
                else:
                    enc.games = [
                        ICGame(overruled=GAMERESULT.FORFEIT_TEAM)
                        for ix in range(PLAYERSPERDIVISION[division])
                    ]
                calc_points(enc)
    await DbICSeries.update(
        {"_id": series.id},
        {
            "rounds": [r.model_dump() for r in series.rounds],
            "teams": [t.model_dump() for t in series.teams],
        },
    )
    logger.info("series updated")
    await calc_standings(series)
    logger.info("standings updated")


async def script_addteam_icseries(
    division: int, index: str | None, name: str, idclub: int, pairingnumber: int
):
    """
    Add a team to a division
    Does not take care of the titulars
    """
    logger.info(f"division: {division}, name: {name}")
    filter = {"division": division, "index": index or ""}
    series = await get_icseries2(filter)
    if not series:
        # create the series and fetch it
        id = await create_icseries(division=division, index=index)
        logger.info(f"id created series {id}")
        s = await get_icseries(id)
    else:
        s = series[0]
    for tm in s.teams:
        if tm.pairingnumber == pairingnumber:
            raise RdBadRequest(description="PairingnumberAlreadyAssigned")
    s.teams.append(
        ICTeam(
            division=division,
            index=index,
            idclub=idclub,
            pairingnumber=pairingnumber,
            name=name,
        )
    )
    await update_icseries(division, index or "", ICSeriesUpdate(teams=s.teams))


async def script_create_encounters():
    """
    create all encounters
    """
    icdata = await load_icdata()
    ss = await get_icseries_all()
    logger.info(f"found {len(ss)} series")
    for s in ss:
        rounds = []
        if s.rounds:
            continue
        logger.info(f"filling series {s.division} {s.index}")
        for r in range(11):  # adding all rounds
            encounters = []
            tm_indexed = {t.pairingnumber: t for t in s.teams}
            for home, visit in ptable[r]:
                enc = ICEncounter(
                    icclub_home=tm_indexed[home].idclub,
                    icclub_visit=tm_indexed[visit].idclub,
                    pairingnr_home=home,
                    pairingnr_visit=visit,
                )
                encounters.append(enc)
            rounds.append(
                ICRound(
                    round=r + 1,
                    rdate=icdata["rounds"][r + 1].isoformat()[0:10],
                    encounters=encounters,
                )
            )
        await update_icseries(s.division, s.index, ICSeriesUpdate(rounds=rounds))
