import numpy as np
import pandas as pd
import pytest

from src.config import PROCESSED_DATA_DIR
from src.scenario_generation.generate_scenarios import (
    CATEGORY_COST_COLUMNS,
    FEATURE_COLUMNS,
    generate_training_dataset,
    sample_apartments,
)

MASTER_PATH = PROCESSED_DATA_DIR / "master_products_features.csv"

pytestmark = pytest.mark.skipif(
    not MASTER_PATH.exists(),
    reason="data/processed/master_products_features.csv not built yet -- run notebooks 01-03 first",
)


@pytest.fixture(scope="module")
def master():
    return pd.read_csv(MASTER_PATH)


def test_sample_apartments_is_reproducible():
    rng1 = np.random.default_rng(42)
    rng2 = np.random.default_rng(42)
    df1 = sample_apartments(50, rng1)
    df2 = sample_apartments(50, rng2)
    pd.testing.assert_frame_equal(df1, df2)


def test_sample_apartments_within_bounds():
    rng = np.random.default_rng(1)
    df = sample_apartments(500, rng)
    assert df["Apartment_Area_m2"].between(50, 260).all()
    assert df["Rooms"].between(1, 5).all()
    assert df["Bathrooms"].ge(1).all()
    assert (df["Master_Bathrooms"] <= df["Bathrooms"]).all()


def test_generate_training_dataset_is_reproducible(master):
    df1 = generate_training_dataset(master, n_scenarios=100, seed=7)
    df2 = generate_training_dataset(master, n_scenarios=100, seed=7)
    pd.testing.assert_frame_equal(df1, df2)


def test_generate_training_dataset_is_valid(master):
    df = generate_training_dataset(master, n_scenarios=200, seed=123)

    assert len(df) == 200
    assert df[FEATURE_COLUMNS].isnull().sum().sum() == 0
    assert (df["Total_Finishing_Cost_EGP"] > 0).all()
    assert df["Scenario_ID"].is_unique

    recomputed_total = df[CATEGORY_COST_COLUMNS].sum(axis=1)
    assert np.allclose(recomputed_total, df["Total_Finishing_Cost_EGP"])


def test_no_leakage_columns_in_features(master):
    leakage_columns = set(CATEGORY_COST_COLUMNS) | {"Total_Finishing_Cost_EGP", "Scenario_ID"}
    assert not (set(FEATURE_COLUMNS) & leakage_columns)


def test_higher_finishing_level_costs_more_on_average(master):
    df = generate_training_dataset(master, n_scenarios=1500, seed=99)
    means = df.groupby("Finishing_Level")["Total_Finishing_Cost_EGP"].mean()
    assert means["Low"] < means["Medium"] < means["High"]
