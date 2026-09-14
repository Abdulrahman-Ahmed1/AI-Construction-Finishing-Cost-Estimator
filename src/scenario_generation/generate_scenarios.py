"""Phases 7-8 -- Apartment scenario generation and training-dataset creation.

============================================================================
WHY THIS MODULE EXISTS (read this before touching the code)
============================================================================
The product master dataset (`data/processed/master_products.csv`) has real
prices for ~6,500 individual construction/finishing products, but it has NO
apartment-level `Total_Finishing_Cost_EGP` -- no dataset of real apartments
with a known total finishing bill exists anywhere in this project's data.

Per the project rules, we do NOT fabricate that number by pretending it was
observed. Instead, this module builds a documented, reproducible SIMULATION:

1. Sample a population of plausible apartment configurations (area, rooms,
   bathrooms, balconies, receptions, finishing-level preference) from
   documented, hand-set (not fitted-to-any-target) distributions that
   reflect typical Egyptian residential apartments.
2. For each apartment, and for every required "line item" implied by its
   configuration (e.g. "N interior doors", "wiring for the whole area",
   "WC + wash basin per bathroom", ...), select ONE real product from the
   master dataset that matches the requested quality tier, and compute the
   quantity needed using that product's OWN `Quantity_Rule` / `Rule_Value`
   (and, where relevant, `Coverage_m2`, `Coverage_m2_per_L`, `Coats`,
   `Waste_Factor`) -- the same quantity-rule vocabulary that was already
   present in the raw data and used by the prior per-category notebooks.
3. Sum every line item's (quantity x price) into a category cost, add
   labor + auxiliary costs (same mechanism), and sum everything into
   `Total_Finishing_Cost_EGP`.

Every apartment is *simulated*, and every simulated apartment's cost is
built entirely from real product prices plus the requirement/quantity logic
that was already encoded in the raw data. Nothing about the target is
invented independently of the source data. This is a SCENARIO-GENERATED /
SYNTHETIC training dataset and is labeled as such everywhere it is used.

============================================================================
DOCUMENTED ASSUMPTIONS (the only "invented" numbers in this module)
============================================================================
- `WALL_AREA_MULTIPLIER = 3.0`: ratio of paintable wall area to floor area.
  Carried over from the prior work's own paints notebook.
- `RECEPTION_AREA_FRACTION = 0.35`: share of the apartment's floor area
  allocated to the reception/living area (the rest is "bedroom" area) --
  needed only to split the Flooring category's Reception vs. Bedroom line
  items, both of which are mandatory and together must cover 100% of the
  apartment area.
- Apartment characteristic distributions in `sample_apartments` (room
  counts, area-per-room-count, bathroom/balcony/reception counts,
  Finishing_Level mix) -- documented inline, chosen to reflect plausible
  Egyptian residential apartments, NOT fitted to any target.
- `OPTIONAL_INCLUDE_PROB`: probability that an optional/upgrade line item
  (e.g. a Reception chandelier, a decorative ceiling, a master-bathroom
  rain shower/sliding cabin) is included, as a function of Finishing_Level.
- `QUALITY_TRANSITION_PROBS`: within one apartment, each category's
  purchased quality tier is usually equal to the apartment's overall
  Finishing_Level, but is allowed to drift up/down one tier with a small
  probability -- real households do not buy perfectly uniform quality
  across every category.

All of these are simple, monotone, documented modeling choices, not fitted
parameters, and are clearly separated from the real product-price data that
drives the actual cost arithmetic.
============================================================================
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import QUALITY_LEVEL_ORDER, RANDOM_SEED

WALL_AREA_MULTIPLIER = 3.0
RECEPTION_AREA_FRACTION = 0.35

OPTIONAL_INCLUDE_PROB = {"Low": 0.10, "Medium": 0.50, "High": 0.85}

# Probability that a given category's purchased quality tier equals the
# apartment's overall Finishing_Level; the remainder is split over the
# existing neighbouring tier(s).
QUALITY_SAME_TIER_PROB = 0.70

CATEGORY_COST_COLUMNS = [
    "Ceilings_Cost", "Doors_Cost", "Electrical_Basic_Cost",
    "Electrical_Finishing_Cost", "Flooring_Cost", "Paints_Cost",
    "Plumbing_Cost", "Sanitary_Cost", "Labor_Cost", "Auxiliary_Cost",
]

# Feature columns that are legitimate model inputs (known before the total
# cost is known). Category cost columns and the target are intentionally
# excluded -- see notebook 05 / the Phase 9 leakage audit.
FEATURE_COLUMNS = [
    "Apartment_Area_m2", "Rooms", "Bathrooms", "Master_Bathrooms",
    "Balconies", "Receptions", "Finishing_Level",
    "Ceilings_Quality", "Doors_Quality", "Electrical_Basic_Quality",
    "Electrical_Finishing_Quality", "Flooring_Quality", "Paints_Quality",
    "Plumbing_Quality", "Sanitary_Quality",
    "Include_Reception_Ceiling_Upgrade", "Include_Reception_Chandelier",
    "Include_Master_Bathroom_Upgrade", "Plumbing_System",
]


def sample_apartments(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Sample `n` plausible apartment configurations.

    All distributions below are documented, hand-set assumptions about the
    Egyptian residential market -- not fitted to any cost target.
    """
    rooms = rng.choice([1, 2, 3, 4, 5], size=n, p=[0.05, 0.30, 0.40, 0.20, 0.05])

    base_area = {1: 55, 2: 85, 3: 120, 4: 160, 5: 200}
    area = np.array([base_area[r] for r in rooms], dtype=float)
    area += rng.normal(0, 12, size=n)
    area = np.clip(area, 50, 260)

    bathrooms = np.empty(n, dtype=int)
    bathrooms[rooms <= 2] = 1
    mask_34 = (rooms == 3) | (rooms == 4)
    bathrooms[mask_34] = rng.choice([1, 2], size=mask_34.sum(), p=[0.35, 0.65])
    mask_5 = rooms == 5
    bathrooms[mask_5] = rng.choice([2, 3], size=mask_5.sum(), p=[0.4, 0.6])

    master_bathrooms = (bathrooms >= 1).astype(int)

    balcony_p = {1: [0.5, 0.4, 0.1, 0.0], 2: [0.3, 0.5, 0.2, 0.0],
                 3: [0.15, 0.45, 0.3, 0.1], 4: [0.05, 0.35, 0.4, 0.2],
                 5: [0.0, 0.2, 0.4, 0.4]}
    balconies = np.array([rng.choice([0, 1, 2, 3], p=balcony_p[r]) for r in rooms])

    receptions = np.where(
        area < 180, 1, rng.choice([1, 2], size=n, p=[0.7, 0.3])
    )

    finishing_level = rng.choice(
        QUALITY_LEVEL_ORDER, size=n, p=[0.30, 0.45, 0.25]
    )

    df = pd.DataFrame({
        "Apartment_Area_m2": area.round(1),
        "Rooms": rooms,
        "Bathrooms": bathrooms,
        "Master_Bathrooms": master_bathrooms,
        "Balconies": balconies,
        "Receptions": receptions,
        "Finishing_Level": finishing_level,
    })
    df["Reception_Area_m2"] = (df["Apartment_Area_m2"] * RECEPTION_AREA_FRACTION).round(1)
    df["Bedroom_Area_m2"] = (df["Apartment_Area_m2"] - df["Reception_Area_m2"]).round(1)
    df["Paintable_Area_m2"] = (df["Apartment_Area_m2"] * WALL_AREA_MULTIPLIER).round(1)
    return df


def _drift_tier(base_level: str, rng: np.random.Generator) -> str:
    """Move 0 or +-1 step away from `base_level` on the Low/Medium/High scale."""
    idx = QUALITY_LEVEL_ORDER.index(base_level)
    options, probs = [idx], [QUALITY_SAME_TIER_PROB]
    neighbours = [j for j in (idx - 1, idx + 1) if 0 <= j < len(QUALITY_LEVEL_ORDER)]
    remaining = 1 - QUALITY_SAME_TIER_PROB
    for j in neighbours:
        options.append(j)
        probs.append(remaining / len(neighbours))
    probs = np.array(probs) / np.sum(probs)
    chosen_idx = rng.choice(options, p=probs)
    return QUALITY_LEVEL_ORDER[chosen_idx]


def _quantity_for_row(row: pd.Series, apt: pd.Series) -> float:
    """Compute the quantity needed for one chosen product, using that
    product's own Quantity_Rule/Rule_Value (+ coverage columns where
    relevant) and the apartment's characteristics. See module docstring."""
    rule = row["Quantity_Rule"]
    rule_value = float(row["Rule_Value"]) if pd.notna(row.get("Rule_Value")) else 1.0
    req_for = row.get("Required_For")

    if rule == "Fixed":
        return rule_value
    if rule == "Per_Room":
        return rule_value * apt["Rooms"]
    if rule == "Per_Bathroom":
        return rule_value * apt["Bathrooms"]
    if rule == "Per_Master_Bathroom":
        return rule_value * apt["Master_Bathrooms"]
    if rule == "Per_Balcony":
        return rule_value * apt["Balconies"]
    if rule == "Per_Reception":
        return rule_value * apt["Receptions"]
    if rule == "Per_Area":
        return rule_value * apt["Apartment_Area_m2"]
    if rule == "Area_m2":
        area = apt["Reception_Area_m2"] if req_for == "Reception" else apt["Bedroom_Area_m2"]
        return rule_value * area
    if rule == "Area_m2/Coverage":
        area = apt["Reception_Area_m2"] if req_for == "Reception" else apt["Apartment_Area_m2"]
        coverage = float(row["Coverage_m2"])
        return rule_value * area / coverage
    if rule == "Paintable_Area/Coverage":
        coats = float(row["Coats"])
        waste = float(row["Waste_Factor"])
        coverage = float(row["Coverage_m2_per_L"])
        return apt["Paintable_Area_m2"] * coats * (1 + waste) / coverage
    if rule == "Category_Specific":
        unit = row.get("Unit")
        if unit == "m2" and req_for == "Flooring":
            return rule_value * apt["Apartment_Area_m2"]
        if unit == "m2" and req_for == "Paints":
            return rule_value * apt["Paintable_Area_m2"]
        if unit == "Bathroom":
            return rule_value * apt["Bathrooms"]
        if unit == "Room":
            return rule_value * (apt["Rooms"] + apt["Receptions"])
        raise ValueError(f"Unhandled Category_Specific row: {row.to_dict()}")
    raise ValueError(f"Unknown Quantity_Rule: {rule!r}")


def _nearest_tier(available: list[str], desired: str) -> str:
    if desired in available:
        return desired
    d_idx = QUALITY_LEVEL_ORDER.index(desired)
    by_distance = sorted(available, key=lambda lvl: abs(QUALITY_LEVEL_ORDER.index(lvl) - d_idx))
    return by_distance[0]


def _pick_product(records_by_tier: dict[str, list[dict]], quality_level: str, rng: np.random.Generator) -> dict:
    """Pick one product (as a plain dict, for fast attribute access) from a
    pre-split-by-quality-tier pool. Pools are split once per slot (see
    `_Slot`), not on every scenario, which is what keeps generation of
    thousands of scenarios fast."""
    tier = _nearest_tier(list(records_by_tier.keys()), quality_level)
    records = records_by_tier[tier]
    idx = rng.integers(0, len(records))
    return records[idx]


class _Slot:
    """One required (or optional) line item in an apartment finishing scenario."""

    __slots__ = ("name", "records_by_tier", "optional", "cost_field", "condition")

    def __init__(self, name, pool, cost_field, optional=False, condition=None):
        self.name = name
        self.records_by_tier = {
            tier: sub.to_dict("records") for tier, sub in pool.groupby("Quality_Level")
        }
        self.optional = optional
        self.cost_field = cost_field
        self.condition = condition or (lambda apt: True)


def _ensure_labor_auxiliary_quantity_fields(master: pd.DataFrame) -> pd.DataFrame:
    """The raw `labor_and_auxiliary.csv` file has no Quantity_Rule/Rule_Value
    columns at all (verified in the Phase 2 audit) -- unlike every other
    category, which already ships with this vocabulary. Documented fix:
    every Labor/Auxiliary line item is assigned Quantity_Rule='Category_Specific'
    with Rule_Value=1.0, and `_quantity_for_row` then dispatches purely on the
    existing `Unit` + `Required_For` columns for this category (see there).
    This mirrors exactly how the user's own prior master-dataset attempt
    (`data/previous_work/master_finishing_products.csv`) filled in the same
    two columns for this category.
    """
    out = master.copy()
    mask = out["Finishing_Category"] == "Labor and Auxiliary"
    out.loc[mask, "Quantity_Rule"] = out.loc[mask, "Quantity_Rule"].fillna("Category_Specific")
    out.loc[mask, "Rule_Value"] = out.loc[mask, "Rule_Value"].fillna(1.0)
    return out


def _build_slots(master: pd.DataFrame) -> list[_Slot]:
    master = _ensure_labor_auxiliary_quantity_fields(master)

    def pool(category, subcats, required_for):
        m = (master["Finishing_Category"] == category) & (master["Required_For"] == required_for)
        if subcats is not None:
            m &= master["Subcategory"].isin(subcats)
        p = master[m]
        if p.empty:
            raise ValueError(f"Empty product pool for {category}/{subcats}/{required_for}")
        return p

    return [
        _Slot("ceiling_base", pool("Ceilings", ["Gypsum Board Ceiling"], "Ceiling"), "Ceilings_Cost"),
        _Slot("ceiling_reception_upgrade", pool("Ceilings", ["Decorative Gypsum Ceiling"], "Reception"),
              "Ceilings_Cost", optional=True),
        _Slot("door_entrance", pool("Doors", ["Entrance"], "Apartment"), "Doors_Cost"),
        _Slot("door_balcony", pool("Doors", ["Balcony"], "Balcony"), "Doors_Cost",
              condition=lambda apt: apt["Balconies"] > 0),
        _Slot("door_interior", pool("Doors", ["Interior"], "Bedroom"), "Doors_Cost"),
        _Slot("elec_wiring_lighting", pool("Electrical Basic", ["Wires & Cables"], "Lighting"), "Electrical_Basic_Cost"),
        _Slot("elec_wiring_sockets", pool("Electrical Basic", ["Wires & Cables"], "Sockets"), "Electrical_Basic_Cost"),
        _Slot("elec_sockets_units", pool("Electrical Basic", ["Sockets"], "Room"), "Electrical_Basic_Cost"),
        _Slot("elec_fin_bedroom_lighting",
              pool("Electrical Finishing", ["LED Bulb", "LED Spotlight"], "Bedroom"), "Electrical_Finishing_Cost"),
        _Slot("elec_fin_reception_downlight",
              pool("Electrical Finishing", ["LED Downlight"], "Reception"), "Electrical_Finishing_Cost"),
        _Slot("elec_fin_reception_chandelier",
              pool("Electrical Finishing", ["Modern Chandelier"], "Reception"), "Electrical_Finishing_Cost",
              optional=True),
        _Slot("flooring_reception", pool("Flooring", ["Floor Tile"], "Reception"), "Flooring_Cost"),
        _Slot("flooring_bedroom", pool("Flooring", ["Floor Tile"], "Bedroom"), "Flooring_Cost"),
        _Slot("paint_walls", pool("Paints", ["Interior"], "Walls"), "Paints_Cost"),
        _Slot("plumbing_pipes", pool("Plumbing Basic", ["PVC Pipes", "PPR Pipes"], "Bathroom"), "Plumbing_Cost"),
        _Slot("sanitary_wc", pool("Sanitary Ware", ["Floor Mounted"], "Bathroom"), "Sanitary_Cost"),
        _Slot("sanitary_basin", pool("Sanitary Ware", ["Pedestal"], "Bathroom"), "Sanitary_Cost"),
        _Slot("sanitary_master_upgrade",
              pool("Sanitary Ware", ["Rain Shower", "Sliding Cabin"], "Master Bathroom"), "Sanitary_Cost",
              optional=True, condition=lambda apt: apt["Master_Bathrooms"] > 0),
        _Slot("labor_flooring_install",
              pool("Labor and Auxiliary", None, "Flooring")[lambda d: d["Category"] == "Labor"], "Labor_Cost"),
        _Slot("aux_flooring_materials",
              pool("Labor and Auxiliary", None, "Flooring")[lambda d: d["Category"] == "Auxiliary"], "Auxiliary_Cost"),
        _Slot("aux_paint_prep",
              pool("Labor and Auxiliary", None, "Paints")[lambda d: d["Category"] == "Auxiliary"], "Auxiliary_Cost"),
        _Slot("labor_paint_apply",
              pool("Labor and Auxiliary", None, "Paints")[lambda d: d["Category"] == "Labor"], "Labor_Cost"),
        _Slot("aux_plumbing_insulation",
              pool("Labor and Auxiliary", None, "Plumbing")[lambda d: d["Category"] == "Auxiliary"], "Auxiliary_Cost"),
        _Slot("labor_plumbing",
              pool("Labor and Auxiliary", None, "Plumbing")[lambda d: d["Category"] == "Labor"], "Labor_Cost"),
        _Slot("labor_electrical",
              pool("Labor and Auxiliary", None, "Electrical")[lambda d: d["Category"] == "Labor"], "Labor_Cost"),
    ]


_SLOT_TO_QUALITY_FEATURE = {
    "ceiling_base": "Ceilings_Quality", "ceiling_reception_upgrade": "Ceilings_Quality",
    "door_entrance": "Doors_Quality", "door_balcony": "Doors_Quality", "door_interior": "Doors_Quality",
    "elec_wiring_lighting": "Electrical_Basic_Quality", "elec_wiring_sockets": "Electrical_Basic_Quality",
    "elec_sockets_units": "Electrical_Basic_Quality",
    "elec_fin_bedroom_lighting": "Electrical_Finishing_Quality",
    "elec_fin_reception_downlight": "Electrical_Finishing_Quality",
    "elec_fin_reception_chandelier": "Electrical_Finishing_Quality",
    "flooring_reception": "Flooring_Quality", "flooring_bedroom": "Flooring_Quality",
    "paint_walls": "Paints_Quality",
    "plumbing_pipes": "Plumbing_Quality",
    "sanitary_wc": "Sanitary_Quality", "sanitary_basin": "Sanitary_Quality",
    "sanitary_master_upgrade": "Sanitary_Quality",
}


def build_scenario_row(apt: pd.Series, slots: list[_Slot], rng: np.random.Generator) -> dict:
    """Resolve every slot for one apartment scenario and return one flat row."""
    row = apt.to_dict()

    quality_by_feature = {
        feat: _drift_tier(apt["Finishing_Level"], rng)
        for feat in set(_SLOT_TO_QUALITY_FEATURE.values())
    }
    row.update(quality_by_feature)

    costs = {c: 0.0 for c in CATEGORY_COST_COLUMNS}
    row["Include_Reception_Ceiling_Upgrade"] = False
    row["Include_Reception_Chandelier"] = False
    row["Include_Master_Bathroom_Upgrade"] = False
    row["Plumbing_System"] = None

    for slot in slots:
        if not slot.condition(apt):
            continue

        if slot.optional:
            prob = OPTIONAL_INCLUDE_PROB[apt["Finishing_Level"]]
            if rng.random() >= prob:
                continue

        quality_feature = _SLOT_TO_QUALITY_FEATURE.get(slot.name)
        quality_level = quality_by_feature[quality_feature] if quality_feature else apt["Finishing_Level"]

        product = _pick_product(slot.records_by_tier, quality_level, rng)
        qty = _quantity_for_row(product, apt)
        cost = qty * float(product["Price_EGP"])
        costs[slot.cost_field] += cost

        if slot.name == "ceiling_reception_upgrade":
            row["Include_Reception_Ceiling_Upgrade"] = True
        elif slot.name == "elec_fin_reception_chandelier":
            row["Include_Reception_Chandelier"] = True
        elif slot.name == "sanitary_master_upgrade":
            row["Include_Master_Bathroom_Upgrade"] = True
        elif slot.name == "plumbing_pipes":
            row["Plumbing_System"] = product["Subcategory"]

    row.update(costs)
    row["Total_Finishing_Cost_EGP"] = round(sum(costs.values()), 2)
    return row


def generate_training_dataset(
    master: pd.DataFrame, n_scenarios: int, seed: int = RANDOM_SEED
) -> pd.DataFrame:
    """Generate the full scenario-based training dataset.

    Returns one row per simulated apartment scenario, with engineered
    apartment/preference features, per-category cost breakdowns, and the
    Total_Finishing_Cost_EGP target. See the module docstring for the full
    methodology and documented assumptions.
    """
    rng = np.random.default_rng(seed)
    apartments = sample_apartments(n_scenarios, rng)
    slots = _build_slots(master)

    rows = [
        build_scenario_row(apt, slots, rng)
        for _, apt in apartments.iterrows()
    ]
    df = pd.DataFrame(rows)
    df.insert(0, "Scenario_ID", [f"S{i:06d}" for i in range(1, len(df) + 1)])
    return df
