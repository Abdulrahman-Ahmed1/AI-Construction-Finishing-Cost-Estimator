"""Deterministic, explainable itemized cost layer for the Streamlit application.

The ML model predicts the total. This engine creates an auditable representative
bill from the same product data and quantity rules, then allocates the ML total
across those line items so the displayed sections always add up exactly to the
model prediction. It is intentionally NOT presented as a second ML prediction.
"""
from __future__ import annotations

from typing import Any
import pandas as pd

from src.scenario_generation.generate_scenarios import _build_slots, _quantity_for_row
from src.config import PROJECT_ROOT

_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "master_products_features.csv"
_CACHE: dict[str, Any] = {}

CATEGORY_NAMES = {
    "Ceilings_Cost": "Ceilings",
    "Doors_Cost": "Doors",
    "Electrical_Basic_Cost": "Basic Electrical",
    "Electrical_Finishing_Cost": "Electrical Finishing",
    "Flooring_Cost": "Flooring",
    "Paints_Cost": "Paints",
    "Plumbing_Cost": "Plumbing",
    "Sanitary_Cost": "Sanitary Ware",
    "Labor_Cost": "Labor",
    "Auxiliary_Cost": "Auxiliary",
}

TOGGLE_BY_SLOT = {
    "ceiling_reception_upgrade": "Include_Reception_Ceiling_Upgrade",
    "elec_fin_reception_chandelier": "Include_Reception_Chandelier",
    "sanitary_master_upgrade": "Include_Master_Bathroom_Upgrade",
}


def _master() -> pd.DataFrame:
    if "master" not in _CACHE:
        _CACHE["master"] = pd.read_csv(_DATA_PATH)
    return _CACHE["master"]


def _median_product(records: list[dict]) -> dict:
    if not records:
        raise ValueError("No product records available for this finishing item.")
    records = sorted(records, key=lambda r: float(r.get("Price_EGP", 0) or 0))
    return records[len(records) // 2]


def build_detailed_estimate(scenario: dict, predicted_total: float) -> dict:
    """Return representative item lines and category totals scaled to prediction."""
    master = _master()
    apt = dict(scenario)
    area = float(apt["Apartment_Area_m2"])
    apt["Reception_Area_m2"] = round(area * 0.35, 1)
    apt["Bedroom_Area_m2"] = round(area - apt["Reception_Area_m2"], 1)
    apt["Paintable_Area_m2"] = round(area * 3.0, 1)
    slots = _build_slots(master)
    raw_lines: list[dict] = []

    for slot in slots:
        if not slot.condition(pd.Series(apt)):
            continue
        toggle = TOGGLE_BY_SLOT.get(slot.name)
        if toggle and not bool(scenario.get(toggle, False)):
            continue
        quality_feature = {
            "ceiling_base": "Ceilings_Quality", "ceiling_reception_upgrade": "Ceilings_Quality",
            "door_entrance": "Doors_Quality", "door_balcony": "Doors_Quality", "door_interior": "Doors_Quality",
            "elec_wiring_lighting": "Electrical_Basic_Quality", "elec_wiring_sockets": "Electrical_Basic_Quality",
            "elec_sockets_units": "Electrical_Basic_Quality", "elec_fin_bedroom_lighting": "Electrical_Finishing_Quality",
            "elec_fin_reception_downlight": "Electrical_Finishing_Quality", "elec_fin_reception_chandelier": "Electrical_Finishing_Quality",
            "flooring_reception": "Flooring_Quality", "flooring_bedroom": "Flooring_Quality", "paint_walls": "Paints_Quality",
            "plumbing_pipes": "Plumbing_Quality", "sanitary_wc": "Sanitary_Quality", "sanitary_basin": "Sanitary_Quality",
            "sanitary_master_upgrade": "Sanitary_Quality",
        }.get(slot.name)
        tier = scenario.get(quality_feature, scenario.get("Finishing_Level", "Medium"))
        records = slot.records_by_tier.get(tier)
        if not records:
            records = next(iter(slot.records_by_tier.values()))
        # Honor the user's plumbing system when choosing the representative pipe product.
        if slot.name == "plumbing_pipes":
            desired = scenario.get("Plumbing_System")
            matching = [r for r in records if r.get("Subcategory") == desired]
            if matching:
                records = matching
        product = _median_product(records)
        qty = float(_quantity_for_row(pd.Series(product), pd.Series(apt)))
        if qty <= 0:
            continue
        raw_cost = qty * float(product["Price_EGP"])
        raw_lines.append({
            "category_key": slot.cost_field,
            "category": CATEGORY_NAMES[slot.cost_field],
            "item": slot.name,
            "product_name": str(product.get("Product_Name", slot.name)),
            "brand": str(product.get("Brand", "")),
            "unit": str(product.get("Unit", "unit")),
            "quantity": round(qty, 2),
            "unit_price_egp": round(float(product["Price_EGP"]), 2),
            "raw_cost": raw_cost,
        })

    raw_total = sum(x["raw_cost"] for x in raw_lines)
    if raw_total <= 0:
        return {"categories": {}, "lines": [], "allocation_method": "No representative line items available."}

    # First scale all representative lines to the ML total.
    scale = float(predicted_total) / raw_total
    for line in raw_lines:
        line["estimated_cost_egp"] = round(line["raw_cost"] * scale, 2)

    # Fix rounding drift on the final line.
    rounded_sum = sum(x["estimated_cost_egp"] for x in raw_lines)
    if raw_lines:
        raw_lines[-1]["estimated_cost_egp"] = round(raw_lines[-1]["estimated_cost_egp"] + predicted_total - rounded_sum, 2)

    categories: dict[str, float] = {}
    for line in raw_lines:
        categories[line["category"]] = round(categories.get(line["category"], 0) + line["estimated_cost_egp"], 2)

    return {
        "categories": categories,
        "lines": raw_lines,
        "allocation_method": (
            "Representative products are selected from the packaged product dataset using the requested quality level and quantity rules. "
            "Their category proportions are scaled to the ML model's predicted total; therefore the displayed itemized estimate sums exactly to the model prediction."
        ),
    }
