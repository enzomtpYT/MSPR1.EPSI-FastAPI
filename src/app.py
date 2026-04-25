from fastapi import APIRouter, FastAPI

import src.models
from src.router import (
    analytics,
    exports,
    product,
    user,
    equipment,
    workout_session,
    meal_log,
    biometrics_log,
)


app = FastAPI()

api = APIRouter(prefix="/api/v0")
api.include_router(analytics.router)
api.include_router(exports.router)
api.include_router(product.router)
api.include_router(user.router)
api.include_router(equipment.router)
api.include_router(workout_session.router)
api.include_router(meal_log.router)
api.include_router(biometrics_log.router)

app.include_router(api)