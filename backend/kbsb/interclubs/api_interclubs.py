import logging
import base64
from fastapi import HTTPException, Depends, APIRouter, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials
from reddevil.core import (
    RdException,
    bearer_schema,
    validate_token,
)

from . import (
    ICRegistration,
    ICEnrollmentIn,
    ICVenueIn,
    ICVenueDB,
    ICClubDB,
    ICClubItem,
    ICGameDetails,
    ICPlanning,
    ICPlayerUpdate,
    ICPlayerValidationError,
    ICResult,
    ICSeries,
    ICSeriesDB,
    ICStandingsDB,
    ICTeam,
    anon_getICteams,
    anon_getICclub,
    anon_getICclubs,
    anon_get_icseries_clubround,
    anon_getICencounterdetails,
    anon_getICstandings,
    anon_getICstandingsArchive,
    anon_getICresultsArchive,
    anon_get_xlsplayerlist,
    clb_getICclub,
    clb_getICseries,
    clb_saveICplanning,
    clb_saveICresults,
    clb_updateICplayers,
    clb_validateICPlayers,
    find_icregistration,
    getICvenues,
    get_bel_report,
    get_fide_report,
    list_eloprocessing,
    list_bel_reports,
    list_fide_reports,
    list_penalties_reports,
    mgmt_get_xlsplayerlists,
    mgmt_saveICresults,
    mgmt_register_teamforfeit,
    mgmt_updateICplayers,
    set_icregistration,
    set_interclubvenues,
    trf_report_phase2,
    trf_report_phase1,
    write_bel_report,
    write_eloprocessing,
    write_fide_report,
    write_penalties_report,
    xls_registrations,
    xls_venues,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/interclubs")

# enrollments


@router.get("/anon/enrollment/{idclub}", response_model=ICRegistration | None)
async def api_find_interclubenrollment(idclub: int):
    """
    return an enrollment by idclub
    """
    logger.debug(f"api_find_interclubenrollment {idclub}")
    try:
        return await find_icregistration(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call find_interclubenrollment")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/clb/enrollment/{idclub}", response_model=ICRegistration)
async def api_clb_set_enrollment(
    idclub: int,
    ie: ICEnrollmentIn,
    bt: BackgroundTasks,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    from kbsb.member import validate_membertoken

    try:
        validate_membertoken(auth)
        return await set_icregistration(idclub, ie, bt)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call clb_set_enrollemnt")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/mgmt/enrollment/{idclub}", response_model=ICRegistration)
async def api_mgmt_set_enrollment(
    idclub: int,
    ie: ICEnrollmentIn,
    bt: BackgroundTasks,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        return await set_icregistration(idclub, ie, bt)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call mgmt_set_enrollment")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/command/xls_registrations")
async def api_xls_registrations(
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    await validate_token(auth)
    try:
        xlsfile = await xls_registrations()
        return {"xls64": base64.b64encode(xlsfile)}
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call xls_registrations")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/clb/enrollment/{idclub}", response_model=ICRegistration)
async def api_set_enrollment(
    idclub: int,
    ie: ICEnrollmentIn,
    bt: BackgroundTasks,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    from kbsb.member import validate_membertoken

    try:
        validate_membertoken(auth)
        # TODO check club autorization
        return await set_icregistration(idclub, ie, bt=bt)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call update_interclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# venues


@router.get("/anon/venue/{idclub}", response_model=ICVenueDB | None)
async def api_find_interclubvenues(idclub: int):
    try:
        logger.info(f"get venues {idclub}")
        a = await getICvenues(idclub)
        logger.info(f"got venues {a}")
        return a
    except RdException as e:
        logger.info(f"get venues failed {e}")
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call find_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/mgmt/venue/{idclub}", response_model=ICVenueDB)
async def api_mgmt_set_interclubvenues(
    idclub: int,
    ivi: ICVenueIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        return await set_interclubvenues(idclub, ivi)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call set_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/command/xls_venues")
async def api_mgmt_xls_venues(
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    await validate_token(auth)
    try:
        xlsfile = await xls_venues()
        return {"xls64": base64.b64encode(xlsfile)}
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call xls_venues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/clb/venue/{idclub}", response_model=ICVenueDB)
async def api_clb_set_icvenues(
    idclub: int,
    ivi: ICVenueIn,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    from kbsb.member import validate_membertoken

    try:
        validate_membertoken(auth)
        return await set_interclubvenues(idclub, ivi)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call set_interclubvenues")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# icteams and icclub


@router.get("/anon/icteams/{idclub}", response_model=list[ICTeam])
async def api_anon_getICteams(idclub: int):
    try:
        return await anon_getICteams(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call anon_getICteams")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/icclub/{idclub}", response_model=ICClubDB)
async def api_anon_getICclub(idclub: int):
    try:
        return await anon_getICclub(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call clb_getICclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/icclub", response_model=list[ICClubItem | None])
async def api_anon_getICclubs():
    try:
        return await anon_getICclubs()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call clb_getICclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/clb/icclub/{idclub}", response_model=ICClubDB | None)
async def api_clb_getICclub(
    idclub: int,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    from kbsb.member import validate_membertoken

    logger.info(f"api_clb_getICclub {idclub} {auth}")
    try:
        validate_membertoken(auth)
        return await clb_getICclub(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call clb_getICclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/icclub/{idclub}", response_model=ICClubDB | None)
async def api_mgmt_getICclub(
    idclub: int,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        return await clb_getICclub(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call mgmt_getICclub")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post(
    "/clb/icclub/{idclub}/validate", response_model=list[ICPlayerValidationError]
)
async def api_clb_validateICplayers(
    idclub: int,
    players: ICPlayerUpdate,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    from kbsb.member import validate_membertoken

    try:
        validate_membertoken(auth)
        return await clb_validateICPlayers(idclub, players)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call clb_validateICPlayers")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post(
    "/mgmt/icclub/{idclub}/validate", response_model=list[ICPlayerValidationError]
)
async def api_mgmt_validateICplayers(
    idclub: int,
    players: ICPlayerUpdate,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        return await clb_validateICPlayers(idclub, players)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call clb_validateICPlayers")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/clb/icclub/{idclub}", status_code=204)
async def api_clb_updateICPlayers(
    idclub: int,
    players: ICPlayerUpdate,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    from kbsb.member import validate_membertoken

    try:
        validate_membertoken(auth)
        await clb_updateICplayers(idclub, players)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call clb_updateICplayers")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/mgmt/icclub/{idclub}", status_code=204)
async def api_mgmt_updateICPlayers(
    idclub: int,
    players: ICPlayerUpdate,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        await mgmt_updateICplayers(idclub, players)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call clb_updateICplayers")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/command/xls_playerlists")
async def api_mgmt_get_xlsplayerlists(
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    await validate_token(auth)
    try:
        xlsfile = await mgmt_get_xlsplayerlists()
        return {"xls64": base64.b64encode(xlsfile)}
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call mgmt_get_xslplayerlists")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/command/xls_playerlist/{idclub}")
async def api_anon_getXlsplayerlist(idclub: int):
    try:
        xlsfile = await anon_get_xlsplayerlist(idclub)
        return {"xls64": base64.b64encode(xlsfile)}
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call mgmt_getXlsAllplayerlist")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# pairings end results


@router.get("/anon/icseries", response_model=list[ICSeries])
async def api_anon_getICseries(idclub: int | None = 0, round: int | None = 0):
    try:
        return await anon_get_icseries_clubround(idclub, round)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call anon_getICseries")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/clb/icseries", response_model=list[ICSeries])
async def api_clb_getICseries(
    idclub: int | None = 0,
    round: int | None = 0,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    from kbsb.member import validate_membertoken

    try:
        validate_membertoken(auth)
        return await clb_getICseries(idclub, round)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call clb_getICseries")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/icseries", response_model=list[ICSeries])
async def api_mgmt_getICseries(
    idclub: int | None = 0,
    round: int | None = 0,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        return await clb_getICseries(idclub, round)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call mgmt_getICseries")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/clb/icplanning", status_code=201)
async def api_clb_saveICplanning(
    icpi: ICPlanning,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    from kbsb.member import validate_membertoken

    try:
        validate_membertoken(auth)
        await clb_saveICplanning(icpi.plannings)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call clb_saveICplanning")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/mgmt/icresults", status_code=201)
async def api_mgmt_saveICresults(
    icri: ICResult,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        await mgmt_saveICresults(icri.results)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call mgmt_saveICresults")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/clb/icresults", status_code=201)
async def api_clb_saveICresults(
    icri: ICResult,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    from kbsb.member import validate_membertoken

    try:
        logger.info("hi")
        validate_membertoken(auth)
        await clb_saveICresults(icri.results)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call clb_saveICresults")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/icresultdetails", response_model=list[ICGameDetails])
async def api_anon_getICencounterdetails(
    division: int,
    index: str,
    round: int,
    icclub_home: int,
    icclub_visit: int,
    pairingnr_home: int,
    pairingnr_visit: int,
):
    try:
        return await anon_getICencounterdetails(
            division=division,
            index=index or "",
            round=round,
            icclub_home=icclub_home,
            icclub_visit=icclub_visit,
            pairingnr_home=pairingnr_home,
            pairingnr_visit=pairingnr_visit,
        )
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call anon_getICencounterdetails")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/icstandings", response_model=list[ICStandingsDB] | None)
async def api_anon_getICstandings(idclub: int | None = 0):
    try:
        return await anon_getICstandings(idclub)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call anon_getICstandings")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/icstandingsarchive", response_model=list[ICStandingsDB] | None)
async def api_anon_getICstandingsArchive(season: str):
    try:
        logger.info(f"get standings archive {season}")
        return await anon_getICstandingsArchive(season)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call anon_getICstandings")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/anon/icresultsarchive", response_model=list[ICSeriesDB] | None)
async def api_anon_getICresultsArchive(season: str, round: int):
    try:
        logger.info(f"get results archive {season} {round}")
        return await anon_getICresultsArchive(season, round)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call anon_getICresultsarchive")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# tean forfait


@router.post("/mgmt/command/teamforfeit/{division}/{index}/{name}", status_code=201)
async def api_mgmt_register_teamforfeit(
    division: int,
    index: str,
    name: str,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    await validate_token(auth)
    try:
        await mgmt_register_teamforfeit(division, index, name)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api register teamdefault")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# trf processing


@router.post("/mgmt/command/trf/phase1", status_code=201)
async def api_trf_phase1(
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    # await validate_token(auth)
    try:
        await trf_report_phase1()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api trf_process_round")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/mgmt/command/trf/phase2", status_code=201)
async def api_trf_phase2(
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    # await validate_token(auth)
    try:
        await trf_report_phase2()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api trf_process_round")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# elo processing


@router.post("/mgmt/command/write_eloprocessing", status_code=201)
async def api_write_eloprocessing_view(
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    await validate_token(auth)
    try:
        return await write_eloprocessing()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api write_eloprocessing_view")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/mgmt/command/list_eloprocessing", response_model=list[str])
async def api_list_eloprocessing(
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    await validate_token(auth)
    try:
        return await list_eloprocessing()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api write_eloprocessing_view")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# bel elo reports


@router.post("/mgmt/command/write_bel_report/{round}/{path_elo}", status_code=201)
async def api_write_belg_report(
    round: int,
    path_elo: str,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        await write_bel_report(round, path_elo)
    except RdException as e:
        logger.info(f"exception {e}")
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api cacl belgelo")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/mgmt/command/list_bel_reports", response_model=list[str])
async def api_list_bel_reports(
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        return await list_bel_reports()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed apilist bel reports")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/command/get_bel_report/{path_elo}")
async def api_get_bel_report(
    path_elo: str,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        report = await get_bel_report(path_elo)
        return {"report": base64.b64encode(report)}
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api call get bel report")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# fide elo reports


@router.post("/mgmt/command/write_fide_report/{round}/{path_elo}", status_code=201)
async def api_write_fide_report(
    round: int,
    path_elo: str,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    await validate_token(auth)
    try:
        await write_fide_report(round, path_elo)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api write_fide_report")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/mgmt/command/list_fide_reports", response_model=list[str])
async def api_list_fide_reports(
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        return await list_fide_reports()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api list fide reports")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/command/get_fide_report/{path_elo}")
async def api_get_fide_report(
    path_elo: str,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        report = await get_fide_report(path_elo)
        return {"report": base64.b64encode(report)}
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api get fide report")
        raise HTTPException(status_code=500, detail="Internal Server Error")


#  penalties


@router.post("/mgmt/command/write_penalties_report/{round}", status_code=201)
async def api_write_penalties_report(
    round: int,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    await validate_token(auth)
    try:
        await write_penalties_report(round)
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api write penalties report")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/mgmt/command/list_penalties_reports", response_model=list[str])
async def api_list_penalties_reports(
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        return await list_penalties_reports()
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api list penalties reports")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/mgmt/command/get_penalties_report/{path}")
async def api_get_penalties_report(
    path: str,
    auth: HTTPAuthorizationCredentials = Depends(bearer_schema),
):
    try:
        await validate_token(auth)
        report = await get_bel_report(path)
        return {"report": base64.b64encode(report)}
    except RdException as e:
        raise HTTPException(status_code=e.status_code, detail=e.description)
    except Exception:
        logger.exception("failed api get penalties report")
        raise HTTPException(status_code=500, detail="Internal Server Error")
