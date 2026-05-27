import json
import time
from fastapi import HTTPException
import httpx
import asyncio

from app.config import config


# класс-ограничитель для запросов к Riot API
class TokenLimiter(object):
    def __init__(self, rate_limit: int, period: int):
        self.max_tokens = rate_limit
        self.tokens = rate_limit
        self.period = period # в секундах
        self.updated_at = int(time.time() * 1000) # timestamp в миллисекундах
        self.lock = asyncio.Lock()

    # функция для использования токена при запросах к Riot API
    async def spending_tokens(self):
        async with self.lock:
            self.refresh_tokens()

            while self.tokens <= 0: # цикл ожидания для пополнения токенов
                await asyncio.sleep(self.period / self.max_tokens)
                self.refresh_tokens()
            
            self.tokens -= 1

    # функция для пополнения токенов
    def refresh_tokens(self):
        time_now = int(time.time() * 1000)
        delta_time = time_now - self.updated_at
        refill = delta_time * (self.max_tokens / self.period)
        
        if refill > 0:
            self.tokens = min(self.max_tokens, self.tokens + refill)
            self.updated_at = time_now


# класс для обращений к Riot API
class RiotClient(object):
    def __init__(self, api_key: str, short_limiter: TokenLimiter, long_limiter: TokenLimiter):
        self.api_key = api_key # ключ разработчика хранится в .env в корневой папке репозитория
        self.http_client = httpx.AsyncClient(timeout=10)
        self.short_limiter = short_limiter
        self.long_limiter = long_limiter

    # функция для GET запросов к Riot API
    async def get(self, url: str, retry_count: int = 4, backoff: int = 1) -> json:
        # трата токенов, чтобы не превысить rate limits от RIot API
        await self.short_limiter.spending_tokens()
        await self.long_limiter.spending_tokens()

        response = await self.http_client.get(url, headers={"X-Riot-Token": self.api_key})

        # проверка если "протух" RIOT_API_KEY
        if response.status_code == 403 or response.status_code == 401:
            raise HTTPException(
                status_code=response.status_code,
                detail="Протух или неверный RIOT_API_KEY, требуется обновить"
            )

        # проверка если данные не найдены со стороны Riot API (пока без обработки MATCH-V5)
        if response.status_code == 400 or response.status_code == 404:
            raise HTTPException(
                status_code=response.status_code,
                detail="Data not found, проверьте введенные данные"
            )

        # проверка если все таки превысились rate limits
        if response.status_code == 429:
            await asyncio.sleep(int(response.headers.get("Retry-After", "1")))
            return await self.get(url)
        
        # проверка если проблема со стороны Riot API, попыток заретраить 4 шт.
        if response.status_code >= 500:
            # если попытки ретраить закончились, то вывести статус код и детали
            if retry_count <= 0:
                raise HTTPException(
                status_code=response.status_code,
                detail="Попытки обратиться к Riot API исчерпаны"
            )
            
            await asyncio.sleep(backoff)

            return await self.get(url, retry_count=retry_count - 1, backoff=backoff * 2)

        response.raise_for_status()
        return response.json()

# создание единого Riot клиента для GET запросов из любого модуля
riot_client = RiotClient(api_key=config.RIOT_API_KEY, 
                         short_limiter=TokenLimiter(rate_limit=19, period=1), # rate_limit меньше фактического, чтобы убрать погрешность
                         long_limiter=TokenLimiter(rate_limit=95, period=120))