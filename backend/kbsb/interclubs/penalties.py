# copyright Ruben Decrop 2012 - 2022

import logging
import asyncio

from datetime import datetime, timezone, timedelta, time
from csv import DictWriter
from io import StringIO, BytesIO
from reddevil.core import RdInternalServerError
from reddevil.filestore.filestore import (
    write_bucket_content,
    read_bucket_content,
    list_bucket_files,
)
from .md_interclubs import (
    DbICSeries,
    ICSeries,
    DbICClub,
    ICClubDB,
    ICRound,
    ICTeam,
)
from .helpers import load_icdata

logger = logging.getLogger(__name__)
icdata = None

allseries = {}
issues = []
playerratings = {}
fideratings = {}
playertitular = {}
allclubs = []
doublepairings = [
    (401, 4, "E", 1, 12),
    (401, 4, "F", 6, 7),
    (401, 5, "H", 1, 2),
    (401, 5, "M", 8, 9),
    (230, 5, "A", 3, 10),
    (230, 5, "O", 6, 7),
    (607, 4, "H", 1, 12),
    (601, 4, "H", 6, 7),
    (601, 5, "J", 6, 7),
    (548, 5, "J", 1, 3),
    (436, 5, "Q", 1, 10),
    (703, 5, "B", 1, 5),
]


async def write_penalties_report(round: int):
    """
    endpoint to write a penalties report
    """
    global icdata
    logger.debug(f"writing penalties report for round {round}")
    icdata = await load_icdata()
    await read_interclubseries()
    await read_interclubratings()
    check_round(round)
    f = StringIO()
    writer = DictWriter(
        f,
        fieldnames=[
            "reason",
            "division",
            "pairingnr",
            "boardnumber",
            "guilty",
            "opponent",
        ],
    )
    writer.writeheader()
    writer.writerows(issues)
    report = f.getvalue()
    logger.debug(f"report: {len(report)}")
    try:
        write_bucket_content(
            f"icn/penalties_R{round}.txt", BytesIO(report.encode("utf-8"))
        )
        logger.info(f"icn/penalties_R{round}.csv report created")
    except Exception as e:
        logger.info(f"failed to write FIDE file icn/penalties_R{round}.csv")
        logger.exception(e)
        raise RdInternalServerError("Failed to write penalties report")


async def list_penalties_reports() -> list[str]:
    """
    endpoint to list the penalties reports in the cloud
    """
    try:
        files = list_bucket_files("icn")
    except Exception as e:
        logger.info("failed to list penalties reports")
        logger.exception(e)
    await asyncio.sleep(0)
    return [f.split("/")[1] for f in files if f.startswith("icn/penalties")]


async def get_penalties_report(path: str) -> str:
    """
    get the content of a penalties report
    """
    try:
        report = read_bucket_content(f"icn/{path}")
    except Exception as e:
        logger.info("failed to list penalties reports")
        logger.exception(e)
    await asyncio.sleep(0)
    return report


def report_issue(series, gameix, pairingnr, opp_pairingnr, reason):
    clubnames = {t.pairingnumber: t.name for t in series.teams}
    if pairingnr and pairingnr not in clubnames:
        logger.info(f"clubnames issue {pairingnr} {clubnames}")
    issues.append(
        {
            "reason": reason,
            "division": f"{series.division}{series.index}",
            "pairingnr": pairingnr,
            "boardnumber": gameix + 1,
            "guilty": clubnames.get(pairingnr, "###"),
            "opponent": clubnames.get(opp_pairingnr, "###"),
        }
    )


def getround(series: ICSeries, rnd: int) -> ICRound:
    for round in series.rounds:
        if round.round == rnd:
            return round
    logger.info(f"We're fucked to get round {rnd} of {series.division}{series.index}")


def getteam(clb, teamname) -> ICTeam:
    for t in clb.teams:
        if t.name == teamname:
            return t
    logger.info(f"We're fucked to get team {teamname}")


async def read_interclubseries():
    logger.info("reading interclub results")
    for s in await DbICSeries.find_multiple({"_model": ICSeries}):
        allseries[(s.division, s.index)] = s


async def read_interclubratings():
    logger.info("reading interclub ratings")
    for clb in await DbICClub.find_multiple({"_model": ICClubDB, "registered": True}):
        allclubs.append(clb)
        for p in clb.players:
            if p.nature in ["assigned", "imported"]:
                playerratings[p.idnumber] = p.assignedrating
                fideratings[p.idnumber] = p.fiderating
                if p.titular:
                    teamix = int(p.titular.split(" ")[-1])
                    team = getteam(clb, p.titular)
                    playertitular[p.idnumber] = {
                        "team": teamix,
                        "division": team.division,
                        "index": team.index,
                        "pairingnumber": team.pairingnumber,
                    }


def check_round(r):
    global issues
    issues = []
    logger.info("checking forfaits")
    check_forfaits(r)
    logger.info("checking signatures")
    check_signatures(r)
    logger.info("checking player order")
    check_order_players(r)
    logger.info("checking average")
    check_average_elo(r)
    logger.info("checking titular")
    check_titular_ok(r)
    logger.info("checking reserves in single series")
    check_reserves_in_single_series(r)
    logger.info("checking reserves elo too high")
    check_reserves_elotoohigh(r)
    logger.info("done")


def check_forfaits(rnd: int):
    for s in allseries.values():
        round = getround(s, rnd)
        for enc in round.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            for ix, g in enumerate(enc.games):
                if g.result in ["1-0 FF", "0-0 FF"]:
                    report_issue(
                        s,
                        ix,
                        enc.pairingnr_visit,
                        enc.pairingnr_home,
                        "forfait away",
                    )
                if g.result in ["0-1 FF", "0-0 FF"]:
                    report_issue(
                        s,
                        ix,
                        enc.pairingnr_home,
                        enc.pairingnr_visit,
                        "forfait home",
                    )


def check_signatures(rnd: int):
    for s in allseries.values():
        round = getround(s, rnd)
        nextday = icdata["rounds"][rnd] + timedelta(days=1)
        homesigndate = datetime.combine(nextday, time(0)).astimezone(timezone.utc)
        visitsigndate = datetime.combine(nextday, time(12)).astimezone(timezone.utc)
        for enc in round.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            if not enc.signhome_ts:
                report_issue(
                    s,
                    -1,
                    enc.pairingnr_home,
                    enc.pairingnr_visit,
                    "signature home missing",
                )
            elif enc.signhome_ts.astimezone(timezone.utc) > homesigndate:
                report_issue(
                    s,
                    -1,
                    enc.pairingnr_home,
                    enc.pairingnr_visit,
                    "signature home too late",
                )
            if not enc.signvisit_ts:
                report_issue(
                    s,
                    -1,
                    enc.pairingnr_visit,
                    enc.pairingnr_home,
                    "signature away missing",
                )
            elif enc.signvisit_ts.astimezone(timezone.utc) > visitsigndate:
                report_issue(
                    s,
                    -1,
                    enc.pairingnr_visit,
                    enc.pairingnr_home,
                    "signature away too late",
                )


def check_order_players(rnd):
    for s in allseries.values():
        round = getround(s, rnd)
        for enc in round.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            rhome = 3000
            rvisit = 3000
            for ix, g in enumerate(enc.games):
                if not g.idnumber_home or not g.idnumber_visit:
                    continue
                newhome = playerratings.get(g.idnumber_home)
                newvisit = playerratings.get(g.idnumber_visit)
                if newhome is None:
                    report_issue(
                        s, ix, enc.pairingnr_home, 0, "home player is not in playerlist"
                    )
                else:
                    if newhome > rhome:
                        report_issue(
                            s, ix, enc.pairingnr_home, 0, "rating order not correct"
                        )
                    rhome = newhome
                if newvisit is None:
                    report_issue(
                        s,
                        ix,
                        enc.pairingnr_visit,
                        0,
                        "visit player is not in playerlist",
                    )
                else:
                    if newvisit > rvisit:
                        report_issue(
                            s, ix, enc.pairingnr_visit, 0, "rating order not correct"
                        )
                    rvisit = newvisit


def check_average_elo(rnd):
    for clb in allclubs:
        avgdivs = {}
        for t in clb.teams:
            serie = allseries[(t.division, t.index)]
            round = getround(serie, rnd)
            encounters = [
                e
                for e in round.encounters
                if t.pairingnumber in (e.pairingnr_home, e.pairingnr_visit)
            ]
            if len(encounters) != 1:
                logger.info(
                    f"We're fucked to get encounter of {t.name} in {serie.division}{serie.index}"
                )
                for ct in clb.teams:
                    logger.info(f"debugging club team {ct}")
                raise RdInternalServerError("No encounters found")
            enc = encounters[0]
            if not enc.icclub_home or not enc.icclub_visit:  # bye
                continue
            if not enc.boardpoint2_home or not enc.boardpoint2_visit:  # not played]
                continue
            if t.pairingnumber == enc.pairingnr_home:
                ratings = [
                    playerratings[g.idnumber_home]
                    for g in enc.games
                    if g.idnumber_home and playerratings.get(g.idnumber_home)
                ]
            if t.pairingnumber == enc.pairingnr_visit:
                ratings = [
                    playerratings[g.idnumber_visit]
                    for g in enc.games
                    if g.idnumber_visit and playerratings.get(g.idnumber_visit)
                ]
            avgdiv = avgdivs.setdefault(serie.division, [])
            if ratings:
                avgdiv.append(sum(ratings) / len(ratings))
        maxdiv2 = max(avgdivs.get(2, [0]))
        maxdiv3 = max(avgdivs.get(3, [0]))
        maxdiv4 = max(avgdivs.get(4, [0]))
        maxdiv5 = max(avgdivs.get(5, [0]))
        mindiv1 = avgdivs.get(1, [3000])[0]
        mindiv2 = min(avgdivs.get(2, [3000]))
        mindiv3 = min(avgdivs.get(3, [3000]))
        if maxdiv2 > mindiv1:
            logger.info(f"{t.idclub} Avg elo too high in division 2")
        if maxdiv3 > min(mindiv1, mindiv2):
            logger.info(f"{t.idclub} Avg elo too high in division 3")
        if maxdiv4 > min(mindiv1, mindiv2, mindiv3):
            logger.info(f"{t.idclub} Avg elo too high in division 4")
        if maxdiv5 > min(mindiv1, mindiv2, mindiv3):
            logger.info(f"{t.idclub} Avg elo too high in division 4")


def check_titular_ok(rnd):
    for s in allseries.values():
        round = getround(s, rnd)
        for enc in round.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            for ix, g in enumerate(enc.games):
                if g.idnumber_home in playertitular:
                    if s.division > playertitular[g.idnumber_home]["division"]:
                        report_issue(
                            s,
                            ix,
                            enc.pairingnr_home,
                            0,
                            "Titular played in a division too low",
                        )
                    if (
                        s.division == playertitular[g.idnumber_home]["division"]
                        and s.index != playertitular[g.idnumber_home]["index"]
                    ):
                        report_issue(
                            s,
                            ix,
                            enc.pairingnr_home,
                            0,
                            "Titular played in wrong series",
                        )
                    if (
                        s.division == playertitular[g.idnumber_home]["division"]
                        and s.index == playertitular[g.idnumber_home]["index"]
                        and enc.pairingnr_home
                        != playertitular[g.idnumber_home]["pairingnumber"]
                    ):
                        report_issue(
                            s,
                            ix,
                            enc.pairingnr_home,
                            0,
                            "Titular played in wrong team in the series",
                        )
                if g.idnumber_visit in playertitular:
                    if s.division > playertitular[g.idnumber_visit]["division"]:
                        report_issue(
                            s,
                            ix,
                            enc.pairingnr_visit,
                            0,
                            "Titular played in a division too low",
                        )
                    if (
                        s.division == playertitular[g.idnumber_visit]["division"]
                        and s.index != playertitular[g.idnumber_visit]["index"]
                    ):
                        report_issue(
                            s,
                            ix,
                            enc.pairingnr_visit,
                            0,
                            "Titular played in wrong series",
                        )
                    if (
                        s.division == playertitular[g.idnumber_visit]["division"]
                        and s.index == playertitular[g.idnumber_visit]["index"]
                        and enc.pairingnr_visit
                        != playertitular[g.idnumber_visit]["pairingnumber"]
                    ):
                        report_issue(
                            s,
                            ix,
                            enc.pairingnr_visit,
                            0,
                            "Titular played in wrong team in the series",
                        )


def check_reserves_in_single_series(r):
    for idclub, division, index, pnr1, pnr2 in doublepairings:
        series = allseries[(division, index)]
        # build up sets of previous players
        players1 = set()
        players2 = set()
        for rr in range(1, r):
            round = getround(series, rr)
            for enc in round.encounters:
                if enc.icclub_home == 0 or enc.icclub_visit == 0:
                    continue
                if pnr1 in (enc.pairingnr_home, enc.pairingnr_visit):
                    for g in enc.games:
                        if pnr1 == enc.pairingnr_home:
                            players1.add(g.idnumber_home)
                        else:
                            players1.add(g.idnumber_visit)
                if pnr2 in (enc.pairingnr_home, enc.pairingnr_visit):
                    for g in enc.games:
                        if pnr2 == enc.pairingnr_home:
                            players2.add(g.idnumber_home)
                        else:
                            players2.add(g.idnumber_visit)
        # now check the players of this round
        round = getround(series, r)
        for enc in round.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            club601 = enc.icclub_home == 601 or enc.icclub_visit == 601
            if pnr1 in (enc.pairingnr_home, enc.pairingnr_visit):
                for ix, g in enumerate(enc.games):
                    if club601:
                        logger.info(f"game pn1 {g.idnumber_home} - {g.idnumber_visit}")
                    if pnr1 == enc.pairingnr_home and g.idnumber_home in players2:
                        report_issue(
                            series,
                            ix,
                            pnr1,
                            0,
                            f"player {g.idnumber_home} already played in other team of series",
                        )
                    elif pnr1 == enc.pairingnr_visit and g.idnumber_visit in players2:
                        report_issue(
                            series,
                            ix,
                            pnr1,
                            0,
                            f"player {g.idnumber_visit} already played in other team of series",
                        )
            if pnr2 in (enc.pairingnr_home, enc.pairingnr_visit):
                for ix, g in enumerate(enc.games):
                    if club601:
                        logger.info(f"game pnr2 {g.idnumber_home} - {g.idnumber_visit}")
                    if pnr2 == enc.pairingnr_home and g.idnumber_home in players1:
                        report_issue(
                            series,
                            ix,
                            pnr2,
                            0,
                            f"player {g.idnumber_home} already played in other team of series",
                        )
                    elif pnr2 == enc.pairingnr_visit and g.idnumber_visit in players1:
                        report_issue(
                            series,
                            ix,
                            pnr2,
                            0,
                            f"player {g.idnumber_visit} already played in other team of series",
                        )


def check_reserves_elotoohigh(r):
    for s in allseries.values():
        maxelo = icdata["max_elo"][s.division]
        round = getround(s, r)
        for enc in round.encounters:
            if enc.icclub_home == 0 or enc.icclub_visit == 0:
                continue
            for ix, g in enumerate(enc.games):
                # skip if player is titular for the team
                t_home = playertitular.get(g.idnumber_home, {})
                if (
                    t_home
                    and t_home["division"] == s.division
                    and t_home["index"] == s.index
                    and t_home["pairingnumber"] == enc.pairingnr_home
                ):
                    continue
                t_visit = playertitular.get(g.idnumber_visit, {})
                if (
                    t_visit
                    and t_visit["division"] == s.division
                    and t_visit["index"] == s.index
                    and t_visit["pairingnumber"] == enc.pairingnr_visit
                ):
                    continue
                # now check the elo
                fide_home = fideratings.get(g.idnumber_home, 0)
                if fide_home > maxelo:
                    report_issue(
                        s, ix, enc.pairingnr_home, 0, "fide rating reserve too high"
                    )
                fide_visit = fideratings.get(g.idnumber_visit, 0)
                if fide_home > maxelo:
                    report_issue(
                        s, ix, enc.pairingnr_home, 0, "fide rating reserve too high"
                    )
                if fide_visit > maxelo:
                    report_issue(
                        s, ix, enc.pairingnr_visit, 0, "fide rating reserve too high"
                    )
