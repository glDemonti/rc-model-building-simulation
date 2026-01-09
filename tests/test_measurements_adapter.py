import pandas as pd
from core.analytics.adapters.measurements_heating_cooling_summary import (
    MeasurementsHeatingCoolingSummaryAdapter,
)


def test_energy_integration_with_variable_dt():
    # Build synthetic dataset with 2-hour intervals
    times = pd.date_range("2024-01-01 00:00", periods=5, freq="2h")
    # Heat/cool in W (cooling can be negative - should work the same)
    heat_W = [1000, 2000, 0, 500, 1500]
    cool_W = [0, 0, -1000, -2000, 0]  # Negative cooling values

    df = pd.DataFrame(
        {
            "ts": times,
            "tout": [0, 1, 2, 3, 4],
            "tin": [20, 21, 22, 23, 24],
            "heat": heat_W,
            "cool": cool_W,
        }
    )

    adapter = MeasurementsHeatingCoolingSummaryAdapter(ebf_area=100.0)
    res = adapter.compute(df, project_id="measurements", time_column="ts")
    summary = res["summary"]

    # Expected energy: sum(P[W]*dt[h])/1000
    # Delta is 2h for each step, last step uses median (2h)
    # Heat: 1000*2 + 2000*2 + 0*2 + 500*2 = 2000+4000+0+1000 = 7000 Wh = 7 kWh
    # + last value 1500*2 = 3000 Wh = 3 kWh, total = 10 kWh
    expected_heat_kWh = 10.0
    # Cool: 0*2 + 0*2 + 1000*2 + 2000*2 = 0+0+2000+4000 = 6000 Wh = 6 kWh
    # + last value 0*2 = 0, total = 6 kWh
    expected_cool_kWh = 6.0

    heat_row = summary[
        (summary["column_name"] == "Heizleistung")
        & (summary["metric"] == "energy_year")
    ]
    cool_row = summary[
        (summary["column_name"] == "Kühlleistung")
        & (summary["metric"] == "energy_year")
    ]

    assert not heat_row.empty
    assert not cool_row.empty
    assert abs(heat_row.iloc[0]["value"] - expected_heat_kWh) < 1e-6
    assert abs(cool_row.iloc[0]["value"] - expected_cool_kWh) < 1e-6
    # Verify units
    assert heat_row.iloc[0]["unit"] == "kWh"
    assert cool_row.iloc[0]["unit"] == "kWh"


def test_units_are_correct():
    """Verify all metrics return the expected units."""
    times = pd.date_range("2024-01-01 00:00", periods=3, freq="1h")
    df = pd.DataFrame(
        {
            "ts": times,
            "tout": [5, 6, 7],
            "tin": [22, 22, 22],
            "heat": [5000, 6000, 5500],  # W
            "cool": [2000, 3000, 2500],  # W
        }
    )

    adapter = MeasurementsHeatingCoolingSummaryAdapter(ebf_area=100.0)
    res = adapter.compute(
        df,
        project_id="test",
        time_column="ts",
        costs_config={"heating_price": 0.15, "cooling_price": 0.20},
    )
    summary = res["summary"]

    # Check all expected units
    expected_units = {
        "power_mean": "kW",
        "power_max": "kW",
        "power_max_timestamp": "datetime",
        "load_specific": "W/m²",
        "energy_year": "kWh",
        "energy_specific": "kWh/m²",
        "costs_year": "CHF",
    }

    for metric, expected_unit in expected_units.items():
        rows = summary[summary["metric"] == metric]
        if not rows.empty:
            actual_unit = rows.iloc[0]["unit"]
            assert (
                actual_unit == expected_unit
            ), f"Metric {metric}: expected unit {expected_unit}, got {actual_unit}"



def test_positive_cooling_values():
    """Test that positive cooling values work correctly (same result as negative)."""
    times = pd.date_range("2024-01-01 00:00", periods=3, freq="1h")
    
    # Test with positive cooling
    df_pos = pd.DataFrame(
        {
            "ts": times,
            "tout": [5, 6, 7],
            "tin": [22, 22, 22],
            "heat": [0, 0, 0],
            "cool": [1000, 2000, 1500],  # Positive
        }
    )
    
    # Test with negative cooling
    df_neg = pd.DataFrame(
        {
            "ts": times,
            "tout": [5, 6, 7],
            "tin": [22, 22, 22],
            "heat": [0, 0, 0],
            "cool": [-1000, -2000, -1500],  # Negative
        }
    )
    
    adapter = MeasurementsHeatingCoolingSummaryAdapter(ebf_area=100.0)
    
    res_pos = adapter.compute(df_pos, project_id="test", time_column="ts")
    res_neg = adapter.compute(df_neg, project_id="test", time_column="ts")
    
    # Extract cooling energy from both
    cool_pos = res_pos["summary"][
        (res_pos["summary"]["column_name"] == "Kühlleistung")
        & (res_pos["summary"]["metric"] == "energy_year")
    ].iloc[0]["value"]
    
    cool_neg = res_neg["summary"][
        (res_neg["summary"]["column_name"] == "Kühlleistung")
        & (res_neg["summary"]["metric"] == "energy_year")
    ].iloc[0]["value"]
    
    # Both should give the same result (absolute value)
    assert abs(cool_pos - cool_neg) < 1e-6
    # And both should be positive
    assert cool_pos > 0
    assert cool_neg > 0

