from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import quote

from app.models import Player
from app.repository import player as player_repository
from app.client.riot_client import riot_client
from app.config import config


# сервис для синхронизации актуальных данных игрока
class SyncService(object):
    # функция для синхронизации игрока по riot id при создании нового игрока в БД или обновления его riot id в БД
    async def sync_player_by_riot_id(self, game_name: str, tag_line: str, db: AsyncSession) -> Player:
        player_account_data = await riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/riot/"
                                                    f"account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}")
        
        player = await player_repository.get_player_by_puuid(player_account_data["puuid"], db)
        # если игрок нашелся в БД по puuid, то обновить его riot id
        if player is not None:
            return await player_repository.update_player_riot_id(player_account_data["puuid"], game_name, tag_line, db)
        
        # дополнительный словарь с данными игрока для БД
        player_summoner_data = await riot_client.get(f"https://{quote(config.PLATFORM_HOST["euw1"])}.api.riotgames.com/lol/"
                                                     f"summoner/v4/summoners/by-puuid/{player_account_data["puuid"]}")
        player_summoner_data |= {"region": config.REGIONAL_HOST["eu"]}
        return await player_repository.create_player(player_account_data, player_summoner_data, db)
    
    # функция для синхронизации игрока по puuid при создании нового игрока в БД
    async def sync_player_by_puuid(self, puuid: str, db: AsyncSession) -> Player:
        player_account_data = await riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/riot/"
                                                    f"account/v1/accounts/by-puuid/{puuid}")
        player_summoner_data = await riot_client.get(f"https://{quote(config.PLATFORM_HOST["euw1"])}.api.riotgames.com/lol/"
                                                     f"summoner/v4/summoners/by-puuid/{puuid}")
        player_summoner_data |= {"region": config.REGIONAL_HOST["eu"]}
        
        return await player_repository.create_player(player_account_data, player_summoner_data, db)


sync_service = SyncService()