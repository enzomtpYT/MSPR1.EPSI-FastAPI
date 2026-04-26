from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.models
from src.seed import seed_database
from src.router import (
    analytics,
    exports,
    product,
    user,
    equipment,
    workout_session,
    meal_log,
    biometrics_log,
    etl
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api/v0")
api.include_router(analytics.router)
api.include_router(exports.router)
api.include_router(product.router)
api.include_router(user.router)
api.include_router(equipment.router)
api.include_router(workout_session.router)
api.include_router(meal_log.router)
api.include_router(biometrics_log.router)
api.include_router(etl.router)

app.include_router(api)


@app.on_event("startup")
def initialize_database() -> None:
    """Apply application bootstrap steps after the schema is available."""
    seed_database()