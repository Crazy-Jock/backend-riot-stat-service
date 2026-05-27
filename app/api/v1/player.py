from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependency import get_db
from app.service import player as player_service

router = APIRouter()


@router.get("/player/{game_name}/{tag_line}")
async def get_player_by_riot_id(game_name: str, tag_line: str, db: AsyncSession = Depends(get_db)):
    return await player_service.get_player_by_riot_id(game_name, tag_line, db)

@router.get("/player/{puuid}")
async def get_player_by_puuid(puuid: str, db: AsyncSession = Depends(get_db)):
    return await player_service.get_player_by_puuid(puuid, db)