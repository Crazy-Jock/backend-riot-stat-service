from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_db
from app.service import admin as admin_service

router = APIRouter()


@router.get("/admin/sync/by-riot-id/{game_name}/{tag_line}")
async def sync_player_by_riot_id(game_name: str, tag_line: str, db: AsyncSession = Depends(get_db)):
    return await admin_service.sync_player_by_riot_id(game_name, tag_line, db)

@router.get("/admin/sync/by-puuid/{puuid}")
async def sync_player_by_puuid(puuid: str, db: AsyncSession = Depends(get_db)):
    return await admin_service.sync_player_by_puuid(puuid, db)

@router.get("/admin/sync/matches/by-puuid/{puuid}")
async def sync_player_matches_by_puuid(puuid: str, count: int, db: AsyncSession = Depends(get_db)):
    return await admin_service.sync_player_matches_by_puuid(puuid, count, db)