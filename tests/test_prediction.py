import pytest

from src.config import MODELS_DIR
from src.prediction.predict import InvalidInputError, predict_finishing_cost, validate_input

MODEL_PATH = MODELS_DIR / "final_model_pipeline.joblib"

VALID_INPUT = {
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


def test_validate_input_accepts_valid_payload():
    cleaned = validate_input(VALID_INPUT)
    assert cleaned["Apartment_Area_m2"] == 120.0
    assert cleaned["Finishing_Level"] == "Medium"


def test_validate_input_rejects_missing_field():
    payload = dict(VALID_INPUT)
    del payload["Plumbing_System"]
    with pytest.raises(InvalidInputError) as exc_info:
        validate_input(payload)
    assert any("Plumbing_System" in e for e in exc_info.value.errors)


def test_validate_input_rejects_out_of_range_area():
    payload = dict(VALID_INPUT)
    payload["Apartment_Area_m2"] = -5
    with pytest.raises(InvalidInputError) as exc_info:
        validate_input(payload)
    assert any("Apartment_Area_m2" in e for e in exc_info.value.errors)


def test_validate_input_rejects_invalid_quality_level():
    payload = dict(VALID_INPUT)
    payload["Finishing_Level"] = "Ultra"
    with pytest.raises(InvalidInputError) as exc_info:
        validate_input(payload)
    assert any("Finishing_Level" in e for e in exc_info.value.errors)


def test_validate_input_rejects_master_bathrooms_exceeding_bathrooms():
    payload = dict(VALID_INPUT)
    payload["Bathrooms"] = 1
    payload["Master_Bathrooms"] = 3
    with pytest.raises(InvalidInputError) as exc_info:
        validate_input(payload)
    assert any("Master_Bathrooms" in e for e in exc_info.value.errors)


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="Trained model not saved yet -- run notebooks 01-06 first")
def test_predict_finishing_cost_returns_expected_shape():
    result = predict_finishing_cost(VALID_INPUT)
    assert result["estimated_total_cost_egp"] > 0
    assert result["prediction_range"]["low_egp"] <= result["estimated_total_cost_egp"] <= result["prediction_range"]["high_egp"]
    assert result["model_version"]


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="Trained model not saved yet -- run notebooks 01-06 first")
def test_predict_finishing_cost_rejects_invalid_input():
    payload = dict(VALID_INPUT)
    payload["Apartment_Area_m2"] = 5000
    with pytest.raises(InvalidInputError):
        predict_finishing_cost(payload)


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="Trained model not saved yet -- run notebooks 01-06 first")
def test_predict_finishing_cost_monotonic_in_finishing_level():
    low = dict(VALID_INPUT)
    high = dict(VALID_INPUT)
    for field in [
        "Finishing_Level", "Ceilings_Quality", "Doors_Quality", "Electrical_Basic_Quality",
        "Electrical_Finishing_Quality", "Flooring_Quality", "Paints_Quality",
        "Plumbing_Quality", "Sanitary_Quality",
    ]:
        low[field] = "Low"
        high[field] = "High"

    low_cost = predict_finishing_cost(low)["estimated_total_cost_egp"]
    high_cost = predict_finishing_cost(high)["estimated_total_cost_egp"]
    assert low_cost < high_cost
