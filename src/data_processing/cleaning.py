"""Phase 3 -- reproducible data cleaning pipeline.

Cleaning is deliberately conservative: the audit (see
reports/01_data_audit_report.md) found the raw data to already be of very
high quality -- no missing core values and no non-positive prices in any of
the 9 raw category files. The issues that WERE found and are handled here:

1. Leading/trailing whitespace on text columns.
2. Exact duplicate rows (verified against the raw files to be true
   duplicates -- identical across every column -- not legitimate repeated
   observations). Counts removed per file are recorded in `.attrs` and
   reported in the audit notebook.
3. One inconsistent vocabulary value: flooring's Required_For used
   "Bedrooms" while every other category used the singular "Bedroom" for
   the same concept.
4. Defensive type coercion of numeric columns and a defensive (belt-and-
   braces) drop of any missing/non-positive Price_EGP, in case a future
   data refresh introduces what the current snapshot does not have.

Outlier handling follows the project rule of never blindly deleting
expensive products: `flag_price_outliers` computes per-category,
per-quality-level IQR bounds and FLAGS rows, it never removes them. A
premium product can legitimately carry a high price within its own
category/quality tier.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.data_processing.audit import numeric_outlier_bounds

# Documented vocabulary fix: same concept, inconsistent spelling.
REQUIRED_FOR_FIXES = {
    "Bedrooms": "Bedroom",
}

NUMERIC_COLUMNS = ["Price_EGP", "Rule_Value", "Quality_Score"]


def clean_category_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the general-purpose cleaning steps to one category dataframe."""
    out = df.copy()

    # 1. Strip whitespace on every text column.
    text_cols = out.select_dtypes(include="object").columns
    for col in text_cols:
        out[col] = out[col].astype("string").str.strip()

    # 2. Standardise known vocabulary inconsistencies.
    if "Required_For" in out.columns:
        out["Required_For"] = out["Required_For"].replace(REQUIRED_FOR_FIXES)

    # 3. Coerce numeric columns (defensive -- raw files already load as
    #    numeric, but a future data refresh could introduce stray strings).
    for col in NUMERIC_COLUMNS:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    # 4. Drop exact duplicate rows.
    before = len(out)
    out = out.drop_duplicates().reset_index(drop=True)
    out.attrs["n_duplicates_removed"] = before - len(out)

    # 5. Defensive validation: remove any row with a missing/non-positive
    #    price. The current snapshot has none (see audit report) but this
    #    keeps the pipeline safe against future, dirtier data.
    if "Price_EGP" in out.columns:
        invalid_price = out["Price_EGP"].isna() | (out["Price_EGP"] <= 0)
        out.attrs["n_invalid_price_removed"] = int(invalid_price.sum())
        if invalid_price.any():
            out = out.loc[~invalid_price].reset_index(drop=True)

    return out


def clean_all(raw: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Clean every raw category dataframe, keyed by filename."""
    return {filename: clean_category_dataframe(df) for filename, df in raw.items()}


def flag_price_outliers(df: pd.DataFrame, group_cols: list[str] | None = None) -> pd.DataFrame:
    """Flag (never remove) price outliers using per-group IQR bounds.

    Grouping by Finishing_Category (+ Quality_Level when available) avoids
    comparing, e.g., a cheap paint's price against an expensive door's price
    on the same global scale, which would flag almost every door as an
    "outlier" for no good reason.
    """
    out = df.copy()
    if group_cols is None:
        group_cols = [c for c in ("Finishing_Category", "Quality_Level") if c in out.columns]

    out["Price_Outlier"] = False
    if not group_cols:
        lower, upper = numeric_outlier_bounds(out["Price_EGP"])
        out["Price_Outlier"] = (out["Price_EGP"] < lower) | (out["Price_EGP"] > upper)
        return out

    for _, idx in out.groupby(group_cols, dropna=False).groups.items():
        group = out.loc[idx, "Price_EGP"]
        lower, upper = numeric_outlier_bounds(group)
        if np.isnan(lower):
            continue
        mask = (group < lower) | (group > upper)
        out.loc[idx, "Price_Outlier"] = mask

    return out
