from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


def get_player_by_riot_id(game_name: str, tag_line: str, db: AsyncSession):
    