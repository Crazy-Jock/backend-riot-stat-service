from sqlalchemy.ext.asyncio import AsyncSession

from app.service.sync import sync_service


# функция синхронизации игрока по riot id
async def sync_player_by_riot_id(game_name: str, tag_line: str, db: AsyncSession):
    await sync_service.sync_player_by_riot_id(game_name, tag_line, db)

    return {"message": "Успешная синхронизация профиля игрока {game_name}#{tag_line}"}

# функция синхронизации игрока по puuid
async def sync_player_by_puuid(puuid: str, db: AsyncSession):
    await sync_service.sync_player_by_puuid(puuid, db)

    return {"message": "Успешная синхронизация профиля игрока",
            "puuid": puuid}

# функция синхронизации последних count матчей игрока по puuid
async def sync_player_matches_by_puuid(puuid: str, count: int, db: AsyncSession):
    await sync_service.sync_player_matches_by_puuid(puuid, count, db)

    return{"message": f"Успешная синхронизация {count} матчей игрока",
           "puuid": puuid}