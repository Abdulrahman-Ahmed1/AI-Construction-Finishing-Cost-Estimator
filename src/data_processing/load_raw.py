"""Loading of raw per-category product CSVs.

These functions only read data/raw/*.csv (copies of the true, untouched
source files) -- they never read from or write to the user's original
"All data" / per-category folders, and they never mutate the files on disk.
"""
from __future__ import annotations

import pandas as pd

from src.config import RAW_CATEGORY_FILES, RAW_DATA_DIR


def load_raw_category(filename: str) -> pd.DataFrame:
    """Load a single raw category CSV and attach its Finishing_Category label."""
    path = RAW_DATA_DIR / filename
    df = pd.read_csv(path)
    label = RAW_CATEGORY_FILES[filename]
    if "Finishing_Category" not in df.columns:
        df.insert(0, "Finishing_Category", label)
    else:
        df["Finishing_Category"] = label
    df["Source_File"] = filename
    return df


def load_all_raw() -> dict[str, pd.DataFrame]:
    """Load every raw category CSV, keyed by filename."""
    return {filename: load_raw_category(filename) for filename in RAW_CATEGORY_FILES}
