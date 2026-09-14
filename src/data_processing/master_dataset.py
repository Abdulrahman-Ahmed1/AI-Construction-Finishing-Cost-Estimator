"""Phase 4 -- Master dataset construction.

Builds a single unified "master products" table from the cleaned per-
category tables. Categories keep their own category-specific columns
(e.g. Ceiling_Type, Power_W, Size_cm, Coverage_m2_per_L, ...); columns that
do not apply to a given category are simply NaN for that category's rows,
rather than being dropped or forced into an unrelated shared column that
would lose meaning.
"""
from __future__ import annotations

import pandas as pd

from src.config import CORE_COLUMNS


def assign_product_ids(df: pd.DataFrame) -> pd.DataFrame:
    """Assign a stable, human-readable Product_ID (P000001, P000002, ...)."""
    out = df.copy()
    out.insert(0, "Product_ID", [f"P{i:06d}" for i in range(1, len(out) + 1)])
    return out


def build_master_dataset(cleaned: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Concatenate all cleaned category tables into one wide master table."""
    frames = [df.copy() for df in cleaned.values()]

    master = pd.concat(frames, axis=0, ignore_index=True, sort=False)
    master = assign_product_ids(master)

    # Column order: documented core schema first (only columns that are
    # actually present), then any remaining category-specific columns.
    present_core = [c for c in CORE_COLUMNS if c in master.columns and c != "Product_ID"]
    other_cols = sorted(
        c for c in master.columns if c not in present_core and c != "Product_ID"
    )
    ordered = ["Product_ID"] + present_core + other_cols
    return master[ordered]
