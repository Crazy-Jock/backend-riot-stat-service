from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import quote

from app.models import Player
from app.repository import player as player_repository
from app.client.riot_client import riot_client
from app.config import config


# сервис для синхронизации актуальных данных игрока
class SyncService(object):
    # функция для синхронизации игрока по riot id при создании нового игрока в БД или обновления его riot id в БД
    async def sync_player_by_riot_id(self, game_name: str, tag_line: str, db: AsyncSession) -> dict: # возвращается dict для использования нужных данных в других service функциях
        player_account_data = await riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/riot/"
                                                    f"account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}")
        
        player = await player_repository.get_player_by_puuid(player_account_data["puuid"], db)
        # если игрок нашелся в БД по puuid, то обновить его riot id
        if player is not None:
            player = await player_repository.update_player_riot_id(player_account_data["puuid"], game_name, tag_line, db)
            return {"player": player}
        
        return await self.sync_player_by_puuid(player_account_data["puuid"], db, player_account_data)
    
    # функция для синхронизации игрока по puuid при создании нового игрока в БД
    async def sync_player_by_puuid(self, puuid: str, db: AsyncSession, player_account_data=None) -> dict: # возвращается dict для использования нужных данных в других service функциях
        # уменьшение запросов к Riot API, если уже произошла первая синхронизация по riot id
        if player_account_data is None:
            player_account_data = await riot_client.get(f"https://{quote(config.REGIONAL_HOST["eu"])}.api.riotgames.com/riot/"
                                                        f"account/v1/accounts/by-puuid/{puuid}")
        player_summoner_data = await riot_client.get(f"https://{quote(config.PLATFORM_HOST["euw1"])}.api.riotgames.com/lol/"
                                                     f"summoner/v4/summoners/by-puuid/{puuid}")
        player_summoner_data |= {"region": config.REGIONAL_HOST["eu"]}
        player_ranked_data = await riot_client.get(f"https://{quote(config.PLATFORM_HOST["euw1"])}.api.riotgames.com/lol/"
                                                   f"league/v4/entries/by-puuid/{puuid}")
        
        player = await player_repository.create_player(player_account_data, player_summoner_data, db)
        ranked = await player_repository.create_ranked(puuid, player_ranked_data, db)

        # словарь для хранения синхронизированных моделей из БД
        sync_dict = {"player": player, "ranked": ranked}
        return sync_dict


sync_service = SyncService()