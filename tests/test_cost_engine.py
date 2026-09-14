from cost_engine.engine import build_detailed_estimate
from src.prediction.predict import predict_finishing_cost


def scenario():
    return {
        "Apartment_Area_m2": 120, "Rooms": 3, "Bathrooms": 2, "Master_Bathrooms": 1,
        "Balconies": 1, "Receptions": 1, "Finishing_Level": "Medium",
        "Ceilings_Quality": "Medium", "Doors_Quality": "Medium",
        "Electrical_Basic_Quality": "Medium", "Electrical_Finishing_Quality": "Medium",
        "Flooring_Quality": "Medium", "Paints_Quality": "Medium",
        "Plumbing_Quality": "Medium", "Sanitary_Quality": "Medium",
        "Include_Reception_Ceiling_Upgrade": True, "Include_Reception_Chandelier": False,
        "Include_Master_Bathroom_Upgrade": True, "Plumbing_System": "PVC Pipes",
    }


def test_detailed_estimate_matches_model_total():
    x = scenario()
    prediction = predict_finishing_cost(x)
    details = build_detailed_estimate(x, prediction["estimated_total_cost_egp"])
    assert details["lines"]
    assert round(sum(details["categories"].values()), 2) == prediction["estimated_total_cost_egp"]
    assert round(sum(x["estimated_cost_egp"] for x in details["lines"]), 2) == prediction["estimated_total_cost_egp"]


def test_detailed_estimate_respects_optional_toggles():
    x = scenario()
    x["Include_Reception_Ceiling_Upgrade"] = False
    x["Include_Reception_Chandelier"] = False
    x["Include_Master_Bathroom_Upgrade"] = False
    prediction = predict_finishing_cost(x)
    details = build_detailed_estimate(x, prediction["estimated_total_cost_egp"])
    names = {line["item"] for line in details["lines"]}
    assert "ceiling_reception_upgrade" not in names
    assert "elec_fin_reception_chandelier" not in names
    assert "sanitary_master_upgrade" not in names
