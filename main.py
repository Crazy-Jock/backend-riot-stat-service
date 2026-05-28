from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import Base, engine
from app.api.v1.player import router as player_router
from app.api.v1.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(player_router, prefix="/api/v1", tags=["player"])
app.include_router(admin_router, prefix="/api/v1", tags=["admin"])