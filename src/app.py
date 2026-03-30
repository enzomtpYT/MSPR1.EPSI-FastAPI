from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from src.database import engine, Base
import src.models
from src.router import (
    analytics,
    product,
    user,
    equipment,
    workout_session,
    meal_log,
    biometrics_log,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

api = APIRouter(prefix="/api/v0")
api.include_router(analytics.router)
api.include_router(product.router)
api.include_router(user.router)
api.include_router(equipment.router)
api.include_router(workout_session.router)
api.include_router(meal_log.router)
api.include_router(biometrics_log.router)

app.include_router(api)