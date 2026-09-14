import pandas as pd

from src.data_processing.cleaning import clean_category_dataframe, flag_price_outliers
from src.data_processing.load_raw import load_all_raw
from src.data_processing.master_dataset import build_master_dataset
from src.config import RAW_CATEGORY_FILES


def test_raw_files_load_with_finishing_category():
    raw = load_all_raw()
    assert set(raw.keys()) == set(RAW_CATEGORY_FILES.keys())
    for filename, df in raw.items():
        assert (df["Finishing_Category"] == RAW_CATEGORY_FILES[filename]).all()
        assert len(df) > 0


def test_cleaning_removes_exact_duplicates():
    df = pd.DataFrame({
        "Price_EGP": [100, 100, 200],
        "Brand": [" A", "A", "B"],
    })
    # Whitespace difference means these two rows are NOT identical before
    # stripping; cleaning should strip first, then dedupe.
    cleaned = clean_category_dataframe(df)
    assert len(cleaned) == 2
    assert cleaned.attrs["n_duplicates_removed"] == 1


def test_cleaning_drops_invalid_prices():
    df = pd.DataFrame({"Price_EGP": [100, 0, -5, None], "Brand": ["A", "B", "C", "D"]})
    cleaned = clean_category_dataframe(df)
    assert (cleaned["Price_EGP"] > 0).all()
    assert cleaned.attrs["n_invalid_price_removed"] == 3


def test_flag_price_outliers_does_not_remove_rows():
    df = pd.DataFrame({
        "Finishing_Category": ["Doors"] * 10,
        "Quality_Level": ["Low"] * 10,
        "Price_EGP": [100, 105, 98, 102, 101, 99, 103, 97, 100, 5000],
    })
    flagged = flag_price_outliers(df)
    assert len(flagged) == len(df)
    assert flagged["Price_Outlier"].sum() >= 1
    assert flagged.loc[flagged["Price_EGP"] == 5000, "Price_Outlier"].iloc[0]


def test_master_dataset_has_unique_product_id_and_no_duplicate_columns():
    raw = load_all_raw()
    cleaned = {k: clean_category_dataframe(v) for k, v in raw.items()}
    master = build_master_dataset(cleaned)

    assert master.columns.tolist().count("Product_ID") == 1
    assert master["Product_ID"].is_unique
    assert (master["Price_EGP"] > 0).all()
    assert set(master["Finishing_Category"].unique()) == set(RAW_CATEGORY_FILES.values())
