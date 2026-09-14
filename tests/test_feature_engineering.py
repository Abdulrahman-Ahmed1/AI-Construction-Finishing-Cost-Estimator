import pandas as pd

from src.feature_engineering.features import (
    add_ceiling_features,
    add_door_features,
    add_flooring_features,
    add_paint_features,
)


def test_flooring_size_parsing():
    df = pd.DataFrame({
        "Finishing_Category": ["Flooring", "Doors"],
        "Size_cm": ["60x120", None],
    })
    out = add_flooring_features(df)
    assert out.loc[0, "Size_Length_cm"] == 60
    assert out.loc[0, "Size_Width_cm"] == 120
    assert out.loc[0, "Tile_Area_m2"] == 0.72


def test_door_size_parsing():
    df = pd.DataFrame({
        "Finishing_Category": ["Doors"],
        "Size": ["100x220 cm"],
    })
    out = add_door_features(df)
    assert out.loc[0, "Size_Width_cm"] == 100
    assert out.loc[0, "Size_Height_cm"] == 220
    assert abs(out.loc[0, "Door_Area_m2"] - 2.2) < 1e-9


def test_paint_liters_required_per_m2():
    df = pd.DataFrame({
        "Finishing_Category": ["Paints"],
        "Coats": [2],
        "Waste_Factor": [0.1],
        "Coverage_m2_per_L": [10.0],
    })
    out = add_paint_features(df)
    # 2 coats * 1.1 waste / 10 coverage = 0.22 L per m2
    assert abs(out.loc[0, "Liters_Required_Per_m2"] - 0.22) < 1e-9


def test_ceiling_panels_per_m2():
    df = pd.DataFrame({
        "Finishing_Category": ["Ceilings"],
        "Coverage_m2": [2.0],
    })
    out = add_ceiling_features(df)
    assert out.loc[0, "Panels_Per_m2"] == 0.5
