from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_db
from app.service import player as player_service

router = APIRouter()


@router.get("/player/by-riot-id/{game_name}/{tag_line}")
async def get_player_by_riot_id(game_name: str, tag_line: str, db: AsyncSession = Depends(get_db)):
    return await player_service.get_player_by_riot_id(game_name, tag_line, db)

@router.get("/player/{puuid}/ranked")
async def get_ranked_entrys(puuid: str, db: AsyncSession = Depends(get_db)):
    return await player_service.get_ranked_entrys(puuid, db)

@router.get("/player/{puuid}/matches")
async def get_matches(puuid: str, db: AsyncSession = Depends(get_db)):
    return await player_service.get_player_matches(puuid, db)

@router.get("/player/{puuid}/champions/")
async def get_champion_stat(puuid: str, champion_name: str | None = None, db: AsyncSession = Depends(get_db)):
    return await player_service.get_champion_stat(puuid, db, champion_name)

@router.get("/matches/{match_id}")
async def get_match_info(match_id: str, db: AsyncSession = Depends(get_db)):
    return await player_service.get_match_by_match_id(match_id, db)

@router.get("/player/{puuid}")
async def get_player_by_puuid(puuid: str, db: AsyncSession = Depends(get_db)):
    return await player_service.get_player_by_puuid(puuid, db)