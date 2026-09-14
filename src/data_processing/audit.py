"""Phase 2 -- Dataset audit utilities.

Produces the profiling information required before any cleaning decision is
made: shape, dtypes, missing values, duplicates, invalid prices, category /
quality-level vocabularies, and basic numerical statistics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class DatasetProfile:
    name: str
    n_rows: int
    n_cols: int
    columns: list[str]
    dtypes: dict[str, str]
    n_duplicates: int
    missing_counts: dict[str, int]
    n_price_missing: int = 0
    n_price_le_zero: int = 0
    price_stats: dict[str, float] = field(default_factory=dict)
    categorical_summary: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_markdown(self) -> str:
        lines = [f"### {self.name}", ""]
        lines.append(f"- Rows: **{self.n_rows}**, Columns: **{self.n_cols}**")
        lines.append(f"- Duplicate rows: **{self.n_duplicates}**")
        if self.price_stats:
            lines.append(
                "- Price_EGP: "
                f"min={self.price_stats.get('min'):.0f}, "
                f"median={self.price_stats.get('50%'):.0f}, "
                f"mean={self.price_stats.get('mean'):.0f}, "
                f"max={self.price_stats.get('max'):.0f}"
            )
            lines.append(
                f"- Price_EGP missing: **{self.n_price_missing}**, "
                f"Price_EGP <= 0: **{self.n_price_le_zero}**"
            )
        missing_nonzero = {k: v for k, v in self.missing_counts.items() if v > 0}
        if missing_nonzero:
            lines.append("- Missing values by column:")
            for col, cnt in sorted(missing_nonzero.items(), key=lambda kv: -kv[1]):
                pct = 100 * cnt / self.n_rows if self.n_rows else 0
                lines.append(f"  - `{col}`: {cnt} ({pct:.1f}%)")
        else:
            lines.append("- Missing values: none")
        lines.append("")
        return "\n".join(lines)


def profile_dataframe(df: pd.DataFrame, name: str) -> DatasetProfile:
    n_rows, n_cols = df.shape
    dtypes = {c: str(t) for c, t in df.dtypes.items()}
    missing_counts = df.isnull().sum().to_dict()
    n_duplicates = int(df.duplicated().sum())

    profile = DatasetProfile(
        name=name,
        n_rows=n_rows,
        n_cols=n_cols,
        columns=list(df.columns),
        dtypes=dtypes,
        n_duplicates=n_duplicates,
        missing_counts={k: int(v) for k, v in missing_counts.items()},
    )

    if "Price_EGP" in df.columns:
        price = pd.to_numeric(df["Price_EGP"], errors="coerce")
        profile.n_price_missing = int(price.isna().sum())
        profile.n_price_le_zero = int((price <= 0).sum())
        desc = price.describe()
        profile.price_stats = {k: float(v) for k, v in desc.items() if k != "count"}

    for col in ("Quality_Level", "Grade", "Quantity_Rule", "Required_For", "Category", "Subcategory"):
        if col in df.columns:
            vc = df[col].value_counts(dropna=False)
            profile.categorical_summary[col] = {str(k): int(v) for k, v in vc.items()}

    return profile


def numeric_outlier_bounds(series: pd.Series, k: float = 1.5) -> tuple[float, float]:
    """Standard Tukey IQR bounds -- used for flagging (not blind deletion)."""
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return (np.nan, np.nan)
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return (q1 - k * iqr, q3 + k * iqr)
