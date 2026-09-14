"""Prediction utilities for the saved finishing-cost model.

The public ``predict_finishing_cost`` function validates a project scenario,
loads the persisted scikit-learn pipeline, predicts the total finishing cost,
and returns a documented empirical prediction range.  It also returns an
*estimated allocation* across finishing categories.  The allocation is not a
second ML prediction and is intentionally separated from the model features to
avoid target leakage: it is derived from category-cost proportions observed in
similar scenario-generated training rows and then scaled to the predicted total.
"""
from __future__ import annotations

import json
from typing import Any

import joblib
import pandas as pd

from src.config import MODELS_DIR, TRAINING_DATA_DIR, QUALITY_LEVEL_ORDER
from src.scenario_generation.generate_scenarios import CATEGORY_COST_COLUMNS, FEATURE_COLUMNS

VALID_QUALITY_LEVELS = set(QUALITY_LEVEL_ORDER)
VALID_PLUMBING_SYSTEMS = {"PVC Pipes", "PPR Pipes"}

_QUALITY_FIELDS = [
    "Finishing_Level", "Ceilings_Quality", "Doors_Quality",
    "Electrical_Basic_Quality", "Electrical_Finishing_Quality",
    "Flooring_Quality", "Paints_Quality", "Plumbing_Quality", "Sanitary_Quality",
]
_BOOLEAN_FIELDS = [
    "Include_Reception_Ceiling_Upgrade", "Include_Reception_Chandelier",
    "Include_Master_Bathroom_Upgrade",
]
_POSITIVE_INT_FIELDS = ["Rooms", "Bathrooms", "Balconies", "Receptions"]

_MODEL_CACHE: dict[str, Any] = {}


class InvalidInputError(ValueError):
    """Raised when input_data fails validation."""
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("Invalid input: " + "; ".join(errors))


def _load_artifacts() -> tuple[Any, dict]:
    if "pipeline" not in _MODEL_CACHE:
        model_path = MODELS_DIR / "final_model_pipeline.joblib"
        metadata_path = MODELS_DIR / "model_metadata.json"
        if not model_path.exists() or not metadata_path.exists():
            raise FileNotFoundError(f"Trained model not found under {MODELS_DIR}.")
        _MODEL_CACHE["pipeline"] = joblib.load(model_path)
        _MODEL_CACHE["metadata"] = json.loads(metadata_path.read_text(encoding="utf-8"))
    return _MODEL_CACHE["pipeline"], _MODEL_CACHE["metadata"]


def _load_training_data() -> pd.DataFrame:
    if "training_data" not in _MODEL_CACHE:
        path = TRAINING_DATA_DIR / "training_dataset.csv"
        if not path.exists():
            raise FileNotFoundError(f"Training dataset required for category allocation not found: {path}")
        _MODEL_CACHE["training_data"] = pd.read_csv(path)
    return _MODEL_CACHE["training_data"]


def clear_model_cache() -> None:
    _MODEL_CACHE.clear()


def validate_input(input_data: dict) -> dict:
    errors: list[str] = []
    cleaned: dict[str, Any] = {}
    missing = [f for f in FEATURE_COLUMNS if f not in input_data or input_data[f] is None]
    if missing:
        errors.append(f"Missing required field(s): {missing}")

    area = input_data.get("Apartment_Area_m2")
    if area is not None:
        try:
            area = float(area)
            if not (20 <= area <= 1000): errors.append("Apartment_Area_m2 must be between 20 and 1000 (sqm)")
        except (TypeError, ValueError): errors.append("Apartment_Area_m2 must be numeric")
        cleaned["Apartment_Area_m2"] = area

    for field in _POSITIVE_INT_FIELDS:
        value = input_data.get(field)
        if value is None: continue
        try:
            value = int(value)
            if value < 0 or value > 20: errors.append(f"{field} must be an integer between 0 and 20")
        except (TypeError, ValueError): errors.append(f"{field} must be an integer")
        cleaned[field] = value

    master_bathrooms = input_data.get("Master_Bathrooms")
    if master_bathrooms is not None:
        try:
            master_bathrooms = int(master_bathrooms)
            if master_bathrooms < 0 or master_bathrooms > 5: errors.append("Master_Bathrooms must be an integer between 0 and 5")
            elif isinstance(cleaned.get("Bathrooms"), int) and master_bathrooms > cleaned["Bathrooms"]: errors.append("Master_Bathrooms cannot exceed Bathrooms")
        except (TypeError, ValueError): errors.append("Master_Bathrooms must be an integer")
        cleaned["Master_Bathrooms"] = master_bathrooms

    for field in _QUALITY_FIELDS:
        value = input_data.get(field)
        if value is not None:
            if value not in VALID_QUALITY_LEVELS: errors.append(f"{field} must be one of {sorted(VALID_QUALITY_LEVELS)}, got {value!r}")
            cleaned[field] = value

    plumbing_system = input_data.get("Plumbing_System")
    if plumbing_system is not None:
        if plumbing_system not in VALID_PLUMBING_SYSTEMS: errors.append(f"Plumbing_System must be one of {sorted(VALID_PLUMBING_SYSTEMS)}, got {plumbing_system!r}")
        cleaned["Plumbing_System"] = plumbing_system

    for field in _BOOLEAN_FIELDS:
        value = input_data.get(field)
        if value is not None:
            if not isinstance(value, bool): errors.append(f"{field} must be a boolean (true/false)")
            cleaned[field] = int(bool(value))

    if errors: raise InvalidInputError(errors)
    return cleaned


def _estimated_category_breakdown(cleaned: dict, predicted_total: float) -> dict[str, float]:
    """Allocate the prediction using observed category-cost proportions from
    similar scenario rows. This is an estimated allocation, not model output."""
    df = _load_training_data()
    subset = df.copy()
    # Prefer rows with same overall level and plumbing system; then progressively
    # relax matching to ensure a stable reference group.
    for col in ("Finishing_Level", "Plumbing_System"):
        if col in subset.columns:
            matched = subset[subset[col] == cleaned[col]]
            if len(matched) >= 30:
                subset = matched
    # Keep roughly similar apartment sizes where possible.
    area = cleaned["Apartment_Area_m2"]
    band = subset[(subset["Apartment_Area_m2"] >= area * 0.8) & (subset["Apartment_Area_m2"] <= area * 1.2)]
    if len(band) >= 30:
        subset = band
    means = subset[CATEGORY_COST_COLUMNS].mean().clip(lower=0)
    total = float(means.sum())
    if total <= 0:
        return {c: 0.0 for c in CATEGORY_COST_COLUMNS}
    allocation = (means / total * predicted_total).round(2)
    return {str(k): float(v) for k, v in allocation.items()}


def predict_finishing_cost(input_data: dict) -> dict:
    pipeline, metadata = _load_artifacts()
    cleaned = validate_input(input_data)
    X = pd.DataFrame([cleaned])[FEATURE_COLUMNS]
    prediction = float(pipeline.predict(X)[0])
    quantiles = metadata.get("test_set_residual_quantiles", {})
    low = prediction + quantiles.get("p05", 0.0)
    high = prediction + quantiles.get("p95", 0.0)
    return {
        "estimated_total_cost_egp": round(prediction, 2),
        "prediction_range": {
            "low_egp": round(max(low, 0.0), 2),
            "high_egp": round(max(high, 0.0), 2),
            "method": "Point prediction shifted by empirical 5th/95th percentile held-out residuals (~90% empirical error band; not a fitted confidence interval).",
        },
        "estimated_category_breakdown": _estimated_category_breakdown(cleaned, prediction),
        "category_breakdown_method": "Estimated allocation from category-cost proportions in similar scenario-generated training rows, normalized to the ML-predicted total. It is not a separate category-cost prediction.",
        "model_version": metadata.get("model_version"),
    }
