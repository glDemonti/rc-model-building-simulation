#!/usr/bin/env python3
"""
Standalone climate station weather data converter.

Converts German climate station CSV files to standardized format
compatible with the RC-Model building simulation tool.

Usage:
    python convert_climate_station.py <input_csv> <output_csv> \
        --latitude <lat> --longitude <lon>

Example:
    python convert_climate_station.py raw_data.csv processed_data.csv \
        --latitude 47.5596 --longitude 7.5922
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import numpy as np


# Import from the core package if running from project root
try:
    from core.solar_utils import (
        SolarLocationManager,
        SolarPositionCalculator,
        SolarRadiationDecomposition,
    )
except ImportError:
    print(
        "Warning: Could not import core utilities. "
        "Running from main package directory.\n"
    )
    sys.path.insert(0, str(Path(__file__).parent))
    from core.solar_utils import (
        SolarLocationManager,
        SolarPositionCalculator,
        SolarRadiationDecomposition,
    )


def detect_csv_format(csv_file: Path) -> str:
    """
    Detect CSV separator (common in German data: semicolon).

    Args:
        csv_file: Path to CSV file

    Returns:
        Detected separator character
    """
    with open(csv_file, "r", encoding="utf-8") as f:
        first_line = f.readline()

    # Count common separators
    if first_line.count(";") > first_line.count(","):
        return ";"
    return ","


def convert_climate_station_csv(
    input_path: Path,
    output_path: Path,
    latitude: float,
    longitude: float,
    start_date: str = None,
) -> bool:
    """
    Convert climate station CSV to standardized weather format.

    Args:
        input_path: Path to input climate station CSV
        output_path: Path for output standardized CSV
        latitude: Station latitude in degrees
        longitude: Station longitude in degrees
        start_date: Optional start date (format: YYYY-MM-DD)

    Returns:
        True if conversion succeeded, False otherwise
    """
    try:
        print(f"Reading climate station file: {input_path}")

        # Detect separator
        separator = detect_csv_format(input_path)
        print(f"Detected separator: {repr(separator)}")

        # Read CSV
        df = pd.read_csv(input_path, sep=separator)
        print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")

        # Create location manager
        location_manager = SolarLocationManager(
            latitude=latitude, longitude=longitude
        )
        print(
            f"Location: {latitude:.4f}°N, {longitude:.4f}°E"
        )

        # Extract required columns with flexible naming
        columns_lower = {col.lower(): col for col in df.columns}

        def get_column_value(possible_names):
            """Get column data using multiple possible names (substring matching)."""
            for name in possible_names:
                for col_key, col_name in columns_lower.items():
                    # Check for substring match (case-insensitive)
                    if name.lower() in col_key:
                        print(f"  Found '{name}' as '{col_name}'")
                        return df[col_name].astype(float)
            raise ValueError(
                f"Required column not found. Tried: {possible_names}"
            )

        print("\nExtracting required columns:")
        air_temperature = get_column_value(
            ["tagesmittel lufttemperatur", "temperatur", "temperature", "temp", "lufttemperatur"]
        )
        relative_humidity = get_column_value(
            ["relative luftfeuchtigkeit", "feuchte", "humidity", "relative humidity", "luftfeuchtigkeit"]
        )
        wind_speed = get_column_value(
            ["windgeschwindigkeit skalar", "windstärke", "wind speed", "windspeed", "windgeschwindigkeit"]
        )
        wind_direction = get_column_value(
            ["windrichtung", "wind direction", "wind_direction"]
        )
        global_radiation = get_column_value(
            [
                "globalstrahlung",
                "globalstrahlung in w/m2",
                "strahlung referenz",
                "global radiation",
                "global_radiation",
                "strahlung global",
            ]
        )

        # Create datetime index
        print("\nProcessing timestamps...")
        datetime_col = None
        for possible_name in ["datum", "time", "datetime", "timestamp"]:
            if possible_name.lower() in columns_lower:
                datetime_col = columns_lower[possible_name.lower()]
                print(f"  Using datetime column: '{datetime_col}'")
                break

        if datetime_col:
            dt = pd.to_datetime(df[datetime_col])
        else:
            # Assume hourly data for one year
            if start_date:
                start = pd.Timestamp(start_date)
                print(f"  No datetime column. Using provided start: {start}")
            else:
                start = pd.Timestamp("2018-01-01 00:00:00")
                print(
                    f"  No datetime column. "
                    f"Using default start: {start}"
                )
            dt = pd.date_range(start=start, periods=len(df), freq="h")

        # Calculate wind components
        print("Calculating wind components...")
        wind_direction_rad = np.radians(wind_direction)
        wind_speed_x = wind_speed * np.cos(wind_direction_rad)
        wind_speed_y = wind_speed * np.sin(wind_direction_rad)

        # Calculate sun position
        print("Calculating sun position...")
        calculator = SolarPositionCalculator(
            location_manager.latitude, location_manager.longitude
        )
        sun_elevation = calculator.calculate_sun_elevation(dt)
        sun_azimuth = calculator.calculate_sun_azimuth(dt)

        # Decompose radiation using Erbs model
        print("Decomposing solar radiation (Erbs model)...")
        (
            solar_radiation_direct,
            solar_radiation_diffuse,
        ) = SolarRadiationDecomposition.decompose_global_radiation(
            global_radiation.values, sun_elevation, dt
        )

        # Sky cover estimation
        sky_cover = np.full(len(df), 0.0)

        # Build standardized DataFrame
        print("Building standardized DataFrame...")
        df_output = pd.DataFrame(
            {
                "timestamp": np.arange(len(df)),
                "air_temperature": air_temperature.values,
                "relative_humidity": relative_humidity.values,
                "wind_speed_x": wind_speed_x.values,
                "wind_speed_y": wind_speed_y.values,
                "solar_radiation_direct": solar_radiation_direct,
                "solar_radiation_diffuse": solar_radiation_diffuse,
                "sky_cover": sky_cover,
                "sun_elevation": sun_elevation,
                "sun_azimuth": sun_azimuth,
            }
        )

        # Write output (CSV for easy inspection/use)
        print(f"\nWriting output to: {output_path}")
        df_output.to_csv(output_path, sep=",", index=False)

        print(f"✓ Conversion successful!")
        print(f"  Input rows: {len(df)}")
        print(f"  Output rows: {len(df_output)}")
        print(
            f"  Output columns: "
            f"{', '.join(df_output.columns)}"
        )

        return True

    except Exception as e:
        print(f"\n✗ Error during conversion:")
        print(f"  {type(e).__name__}: {e}", file=sys.stderr)
        return False


def main():
    """Command-line interface for climate station converter."""
    parser = argparse.ArgumentParser(
        description=(
            "Convert German climate station CSV files to standardized "
            "weather format for RC-Model simulations."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Using explicit coordinates
  %(prog)s station_data.csv weather_processed.csv \\
    --latitude 47.5596 --longitude 7.5922

  # With custom start date (for data without datetime column)
  %(prog)s station_data.csv weather_processed.csv \\
    --latitude 47.5596 --longitude 7.5922 \\
    --start-date 2023-01-01""",
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input climate station CSV file (German format with ; separator)",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Output standardized CSV file (ready for tool upload)",
    )
    parser.add_argument(
        "--latitude",
        type=float,
        required=True,
        help="Station latitude in degrees decimal (e.g., 47.5596)",
    )
    parser.add_argument(
        "--longitude",
        type=float,
        required=True,
        help="Station longitude in degrees decimal (e.g., 7.5922)",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Start date for hourly data (YYYY-MM-DD). "
        "Default: 2018-01-01",
    )

    args = parser.parse_args()

    # Validate input file
    if not args.input.exists():
        print(
            f"✗ Input file not found: {args.input}", file=sys.stderr
        )
        return 1

    if not args.input.is_file():
        print(
            f"✗ Input path is not a file: {args.input}",
            file=sys.stderr,
        )
        return 1

    # Run conversion
    success = convert_climate_station_csv(
        input_path=args.input,
        output_path=args.output,
        latitude=args.latitude,
        longitude=args.longitude,
        start_date=args.start_date,
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
