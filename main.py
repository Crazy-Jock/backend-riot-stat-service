from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.api.v1.player import router as wallet_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(wallet_router, prefix="/api/v1", tags=["wallet"])
