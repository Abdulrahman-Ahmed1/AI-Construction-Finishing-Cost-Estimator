"""Phase 20 -- FastAPI deployment.

Run locally with:

    uvicorn src.api.main:app --reload

The API never retrains the model -- it only loads the pipeline that
notebook 06 already trained and saved to `models/final_model_pipeline.joblib`.
Business-rule validation (ranges, valid categories, cross-field checks)
lives in `src.prediction.predict.validate_input` and is reused as-is here,
so the API, the inference notebook, and the test suite all validate input
identically.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.prediction.predict import (
    InvalidInputError,
    _load_artifacts,
    predict_finishing_cost,
)

logger = logging.getLogger("finishing_cost_api")

app = FastAPI(
    title="AI Construction Finishing Cost Estimation API",
    description=(
        "Estimates the total finishing cost (EGP) of an apartment from its "
        "characteristics and finishing/quality preferences. The model was "
        "trained on a documented, scenario-generated dataset -- see "
        "src/scenario_generation/generate_scenarios.py."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ApartmentInput(BaseModel):
    Apartment_Area_m2: float = Field(..., description="Apartment area in square meters")
    Rooms: int = Field(..., description="Number of bedrooms")
    Bathrooms: int = Field(..., description="Number of bathrooms")
    Master_Bathrooms: int = Field(..., description="Number of master bathrooms (<= Bathrooms)")
    Balconies: int = Field(..., description="Number of balconies")
    Receptions: int = Field(..., description="Number of reception/living areas")
    Finishing_Level: str = Field(..., description="Overall finishing level: Low, Medium, or High")
    Ceilings_Quality: str
    Doors_Quality: str
    Electrical_Basic_Quality: str
    Electrical_Finishing_Quality: str
    Flooring_Quality: str
    Paints_Quality: str
    Plumbing_Quality: str
    Sanitary_Quality: str
    Include_Reception_Ceiling_Upgrade: bool
    Include_Reception_Chandelier: bool
    Include_Master_Bathroom_Upgrade: bool
    Plumbing_System: str = Field(..., description="PVC Pipes or PPR Pipes")

    model_config = {
        "json_schema_extra": {
            "example": {
                "Apartment_Area_m2": 120,
                "Rooms": 3,
                "Bathrooms": 2,
                "Master_Bathrooms": 1,
                "Balconies": 1,
                "Receptions": 1,
                "Finishing_Level": "Medium",
                "Ceilings_Quality": "Medium",
                "Doors_Quality": "Medium",
                "Electrical_Basic_Quality": "Medium",
                "Electrical_Finishing_Quality": "Medium",
                "Flooring_Quality": "Medium",
                "Paints_Quality": "Medium",
                "Plumbing_Quality": "Medium",
                "Sanitary_Quality": "Medium",
                "Include_Reception_Ceiling_Upgrade": True,
                "Include_Reception_Chandelier": False,
                "Include_Master_Bathroom_Upgrade": True,
                "Plumbing_System": "PVC Pipes",
            }
        }
    }


class PredictionRange(BaseModel):
    low_egp: float
    high_egp: float
    method: str


class PredictionResponse(BaseModel):
    estimated_total_cost_egp: float
    prediction_range: PredictionRange
    estimated_category_breakdown: dict[str, float]
    category_breakdown_method: str
    model_version: Optional[str]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eagerly load the model once at startup (never retrains)."""
    try:
        _load_artifacts()
        logger.info("Model loaded successfully at startup.")
    except FileNotFoundError as exc:
        logger.warning("Model not available at startup: %s", exc)
    yield


app.router.lifespan_context = lifespan


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    try:
        _load_artifacts()
        return HealthResponse(status="ok", model_loaded=True)
    except FileNotFoundError:
        return HealthResponse(status="degraded", model_loaded=False)


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: ApartmentInput) -> PredictionResponse:
    try:
        result = predict_finishing_cost(payload.model_dump())
    except InvalidInputError as exc:
        raise HTTPException(status_code=400, detail=exc.errors) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error while predicting")
        raise HTTPException(status_code=500, detail="Internal error while predicting") from exc

    return PredictionResponse(**result)
