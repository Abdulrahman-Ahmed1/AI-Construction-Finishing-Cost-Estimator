"""Phase 6 -- Feature engineering on the product master dataset.

Every feature below has a specific, documented reason and is derived only
from physical/catalog attributes that already exist in the raw data -- none
of them are derived from `Price_EGP`, so none of them leak the product's own
price back in as a feature (see the flooring notebook's own leakage note,
which this module follows).

Features added:

- Flooring: `Size_Length_cm`, `Size_Width_cm` (parsed from `Size_cm`, e.g.
  "60x120") and `Tile_Area_m2` -- physical tile format, useful for EDA and
  for sanity-checking `Area_m2` quantity assumptions.
- Doors: `Size_Height_cm`, `Size_Width_cm` (parsed from `Size`, e.g.
  "100x220 cm") and `Door_Area_m2` -- same rationale.
- Paints: `Liters_Required_Per_m2` = `Coats * (1 + Waste_Factor) /
  Coverage_m2_per_L` -- how many liters of paint one m2 of wall needs for
  the whole job (coats + waste); this is exactly the multiplier the
  scenario generator (Phase 8) needs, derived once here so it is documented
  and testable in one place.
- Ceilings: `Panels_Per_m2` = `1 / Coverage_m2` -- how many ceiling
  units/sheets one m2 of ceiling needs; same rationale as above.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

_SIZE_PATTERN = r"(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)"


def _parse_two_dims(series: pd.Series) -> pd.DataFrame:
    extracted = series.astype("string").str.extract(_SIZE_PATTERN)
    return extracted.astype(float)


def add_flooring_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    mask = out["Finishing_Category"] == "Flooring"
    if mask.any() and "Size_cm" in out.columns:
        dims = _parse_two_dims(out.loc[mask, "Size_cm"])
        out.loc[mask, "Size_Length_cm"] = dims[0].to_numpy()
        out.loc[mask, "Size_Width_cm"] = dims[1].to_numpy()
        out.loc[mask, "Tile_Area_m2"] = (
            out.loc[mask, "Size_Length_cm"] * out.loc[mask, "Size_Width_cm"] / 10_000
        )
    return out


def add_door_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    mask = out["Finishing_Category"] == "Doors"
    if mask.any() and "Size" in out.columns:
        dims = _parse_two_dims(out.loc[mask, "Size"])
        out.loc[mask, "Size_Width_cm"] = dims[0].to_numpy()
        out.loc[mask, "Size_Height_cm"] = dims[1].to_numpy()
        out.loc[mask, "Door_Area_m2"] = (
            out.loc[mask, "Size_Width_cm"] * out.loc[mask, "Size_Height_cm"] / 10_000
        )
    return out


def add_paint_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    mask = out["Finishing_Category"] == "Paints"
    needed = {"Coats", "Waste_Factor", "Coverage_m2_per_L"}
    if mask.any() and needed.issubset(out.columns):
        out.loc[mask, "Liters_Required_Per_m2"] = (
            out.loc[mask, "Coats"]
            * (1 + out.loc[mask, "Waste_Factor"])
            / out.loc[mask, "Coverage_m2_per_L"]
        )
    return out


def add_ceiling_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    mask = out["Finishing_Category"] == "Ceilings"
    if mask.any() and "Coverage_m2" in out.columns:
        coverage = out.loc[mask, "Coverage_m2"].replace(0, np.nan)
        out.loc[mask, "Panels_Per_m2"] = 1 / coverage
    return out


def engineer_features(master: pd.DataFrame) -> pd.DataFrame:
    """Apply every category-specific feature engineering step."""
    out = master.copy()
    out = add_flooring_features(out)
    out = add_door_features(out)
    out = add_paint_features(out)
    out = add_ceiling_features(out)
    return out
