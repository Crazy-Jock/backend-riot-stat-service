import os
import httpx
import asyncio

from dotenv import load_dotenv
from pathlib import Path



class RiotClient(object):
    def __init__(self, api_key: str, bucket: None):
        base_directory = Path(__file__).resolve().parent.parent
        load_dotenv(base_directory / ".env")
        self.api_key = os.getenv("RIOT_API_KEY")
        self.http_client = httpx.AsyncClient(timeout=9)

    async def get(self, url: str):
        pass