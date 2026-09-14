"""Project-wide configuration: paths, constants and reproducibility settings.

All paths are resolved relative to the project root (the parent directory of
this ``src`` package), so the project runs unmodified on any machine as long
as the folder structure is preserved. Never hard-code machine-specific
absolute paths anywhere else in the project -- import them from here instead.
"""
from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Core paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
TRAINING_DATA_DIR = DATA_DIR / "training"
PREVIOUS_WORK_DIR = DATA_DIR / "previous_work"

MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

for _d in (RAW_DATA_DIR, PROCESSED_DATA_DIR, TRAINING_DATA_DIR, MODELS_DIR, REPORTS_DIR, FIGURES_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# Raw source files -> Finishing_Category label.
#
# NOTE ON PROVENANCE (see reports/01_data_audit_report.md for full detail):
# The files under data/raw/ are COPIES of the plain per-category CSVs found
# in this user's individual category working folders (e.g. ceilings_gypsum/,
# Doors/, Flooring/, ...), which is where the *actual* untouched raw product
# data lives. The files that were sitting in the "All data" folder were
# verified byte-for-byte identical to the "*_model_ready"/"*_ml_ready"
# outputs of that same folder's notebook -- i.e. they are already-cleaned,
# already-feature-engineered products of a prior pipeline, not raw data.
# They are preserved untouched under data/previous_work/ and used only as a
# reference for validating this project's own cleaning/feature engineering.
# ---------------------------------------------------------------------------
RAW_CATEGORY_FILES: dict[str, str] = {
    "ceilings_gypsum.csv": "Ceilings",
    "doors.csv": "Doors",
    "electrical_basic.csv": "Electrical Basic",
    "electrical_finishing.csv": "Electrical Finishing",
    "flooring.csv": "Flooring",
    "paints.csv": "Paints",
    "plumbing_basic.csv": "Plumbing Basic",
    "sanitary_ware.csv": "Sanitary Ware",
    "labor_and_auxiliary.csv": "Labor and Auxiliary",
}

# Canonical schema shared, in intent, across every category (not every
# column exists in every raw file -- absence is preserved as NaN rather than
# silently dropped).
CORE_COLUMNS: list[str] = [
    "Product_ID",
    "Finishing_Category",
    "Category",
    "Subcategory",
    "Product_Name",
    "Brand",
    "Material",
    "Product_Type",
    "Quality_Level",
    "Quality_Score",
    "Grade",
    "Quality_Price_Band",
    "Price_EGP",
    "Unit",
    "Quantity_Rule",
    "Rule_Value",
    "Required_For",
    "Optional",
    "Application",
    "Specification",
]

# Standardised Quality_Level vocabulary that every category is mapped onto
# during cleaning (see src/data_processing/cleaning.py). Documented instead
# of silently reinterpreted.
QUALITY_LEVEL_ORDER: list[str] = ["Low", "Medium", "High"]

TARGET_COLUMN = "Total_Finishing_Cost_EGP"
