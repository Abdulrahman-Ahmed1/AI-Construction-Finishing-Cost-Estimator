import pytest
from fastapi.testclient import TestClient

from src.config import MODELS_DIR

MODEL_PATH = MODELS_DIR / "final_model_pipeline.joblib"

pytestmark = pytest.mark.skipif(
    not MODEL_PATH.exists(), reason="Trained model not saved yet -- run notebooks 01-06 first"
)

VALID_PAYLOAD = {
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


@pytest.fixture()
def client():
    from src.api.main import app
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True


def test_predict_endpoint_valid_payload(client):
    response = client.post("/predict", json=VALID_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["estimated_total_cost_egp"] > 0
    assert "low_egp" in body["prediction_range"]


def test_predict_endpoint_missing_field_returns_422(client):
    payload = dict(VALID_PAYLOAD)
    del payload["Apartment_Area_m2"]
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # pydantic-level: required field missing


def test_predict_endpoint_invalid_business_rule_returns_400(client):
    payload = dict(VALID_PAYLOAD)
    payload["Apartment_Area_m2"] = 5000  # valid type, but out of the accepted range
    response = client.post("/predict", json=payload)
    assert response.status_code == 400
    assert "Apartment_Area_m2" in str(response.json()["detail"])


def test_predict_endpoint_invalid_quality_level_returns_400(client):
    payload = dict(VALID_PAYLOAD)
    payload["Finishing_Level"] = "Ultra"
    response = client.post("/predict", json=payload)
    assert response.status_code == 400
