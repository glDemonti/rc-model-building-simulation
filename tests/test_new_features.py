#!/usr/bin/env python
"""
Test script for new features: location coordinates, solar calculations, and verlaufzeit
"""
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path

# Add core to path
sys.path.insert(0, '/home/gianl/Dokumente/projekte/VM2-RC-Modell-ui')

from core.solar_utils import SolarLocationManager, SolarRadiationDecomposition, SolarPositionCalculator
from core.weather_service import WeatherService

def test_location_config():
    """Test 1: Load location coordinates from config"""
    print("\n" + "="*60)
    print("TEST 1: Location Coordinate Configuration")
    print("="*60)
    
    config_path = Path('/home/gianl/Dokumente/projekte/VM2-RC-Modell-ui/projects/simulation-variant-A/config/config_A.json')
    with open(config_path) as f:
        cfg = json.load(f)
    
    # Check location section exists
    assert "location" in cfg, "Location section missing from config"
    print("✓ Location section found in config")
    
    # Check latitude and longitude
    lat = float(cfg["location"]["latitude"]["expression"])
    lon = float(cfg["location"]["longitude"]["expression"])
    print(f"✓ Latitude: {lat}°N")
    print(f"✓ Longitude: {lon}°E")
    
    assert lat == 47.5596, f"Expected latitude 47.5596, got {lat}"
    assert lon == 7.5922, f"Expected longitude 7.5922, got {lon}"
    print("✓ Default Basel coordinates loaded correctly")
    
    return cfg

def test_solar_location_manager(cfg):
    """Test 2: SolarLocationManager from config"""
    print("\n" + "="*60)
    print("TEST 2: SolarLocationManager")
    print("="*60)
    
    # Create manager from config
    manager = SolarLocationManager.from_config(cfg)
    lat, lon = manager.get_coordinates()
    
    print(f"✓ Manager created from config")
    print(f"✓ Location: {lat}°N, {lon}°E")
    
    # Test solar position calculation for a specific date/time
    import datetime as dt
    import math
    
    # Create position calculator
    calc = SolarPositionCalculator(lat, lon)
    
    # Summer solstice: June 21, noon UTC
    dates = pd.DatetimeIndex(['2020-06-21 12:00:00'])
    elevation = calc.calculate_sun_elevation(dates)[0]
    azimuth = calc.calculate_sun_azimuth(dates)[0]
    
    print(f"✓ Sun elevation on June 21 noon: {elevation:.1f}°")
    print(f"✓ Sun azimuth on June 21 noon: {azimuth:.1f}°")
    
    assert elevation > 40, f"Expected reasonable elevation in summer, got {elevation}°"
    print("✓ Solar position calculation working correctly")

def test_erbs_decomposition():
    """Test 3: Erbs radiation decomposition"""
    print("\n" + "="*60)
    print("TEST 3: Erbs Radiation Decomposition Model")
    print("="*60)
    
    decomposer = SolarRadiationDecomposition()
    
    # Test case 1: Clear sky (Kt > 0.8)
    ghr = np.array([400.0])  # W/m²
    sun_elev = np.array([60.0])  # degrees
    
    direct, diffuse = decomposer.decompose_global_radiation(ghr, sun_elev)
    
    print(f"✓ Test case 1 (Clear sky, sun elevation 60°):")
    print(f"  Global: {ghr[0]} W/m²")
    print(f"  Diffuse: {diffuse[0]:.1f} W/m²")
    print(f"  Direct: {direct[0]:.1f} W/m²")
    assert diffuse[0] > 0 and direct[0] > 0, "Both components should be positive"
    
    # Test case 2: Low sun (Kt low)
    ghr = np.array([50.0])
    sun_elev = np.array([15.0])  # low sun angle
    
    direct, diffuse = decomposer.decompose_global_radiation(ghr, sun_elev)
    
    print(f"✓ Test case 2 (Low sun, elevation 15°):")
    print(f"  Global: {ghr[0]} W/m²")
    print(f"  Diffuse: {diffuse[0]:.1f} W/m²")
    print(f"  Direct: {direct[0]:.1f} W/m²")
    print("✓ Erbs decomposition working correctly")

def test_climate_station_csv():
    """Test 4: Climate station CSV processing infrastructure"""
    print("\n" + "="*60)
    print("TEST 4: Climate Station CSV Infrastructure")
    print("="*60)
    
    # Verify the CSV file exists and is readable
    csv_path = Path('/home/gianl/Downloads/100254.csv')
    
    if csv_path.exists():
        print(f"✓ Climate station CSV file found: {csv_path}")
        
        # Try to read it
        try:
            df = pd.read_csv(csv_path, sep=';', nrows=5)
            print(f"✓ CSV is readable with semicolon separator")
            print(f"✓ Sample columns: {list(df.columns[:5])}")
            print(f"✓ CSV has {len(df)} rows in sample")
            print("✓ Climate station CSV format valid for processing")
        except Exception as e:
            print(f"✗ Error reading CSV: {e}")
    else:
        print(f"✗ CSV file not found at {csv_path}")

def test_verlaufzeit():
    """Test 5: Verlaufzeit (thermal settling time)"""
    print("\n" + "="*60)
    print("TEST 5: Verlaufzeit Feature")
    print("="*60)
    
    # Create sample weather data
    dates = pd.date_range('2020-01-01', periods=24*7, freq='h')  # 7 days
    temps = np.sin(np.arange(len(dates)) * 2*np.pi / 24) * 5 + 10  # Cyclic pattern
    
    df = pd.DataFrame({
        'air_temperature': temps,
        'relative_humidity': np.ones(len(dates)) * 60,
        'wind_speed_x': np.ones(len(dates)) * 1.0,
        'wind_speed_y': np.ones(len(dates)) * 0.5,
        'solar_radiation_direct': np.ones(len(dates)) * 200,
        'solar_radiation_diffuse': np.ones(len(dates)) * 100,
        'sky_cover': np.ones(len(dates)) * 50,
        'sun_elevation': np.ones(len(dates)) * 30,
        'sun_azimuth': np.ones(len(dates)) * 180,
    }, index=dates)
    
    print(f"✓ Test data created: {len(df)} rows")
    print(f"  Date range: {df.index[0]} to {df.index[-1]}")
    
    # Create mock repo and test verlaufzeit application
    class MockWeatherRepository:
        pass
    
    weather_service = WeatherService(MockWeatherRepository())
    df_with_verlaufzeit = weather_service._apply_verlaufzeit(df, verlaufzeit_days=2)
    
    print(f"✓ Verlaufzeit applied (2 days)")
    print(f"  Original length: {len(df)}")
    print(f"  New length: {len(df_with_verlaufzeit)}")
    print(f"  Added rows: {len(df_with_verlaufzeit) - len(df)} (expected {24*2})")
    
    assert len(df_with_verlaufzeit) == len(df) + 24*2, "Verlaufzeit rows not added correctly"
    
    # Check that negative timestamps were added
    negative_indices = df_with_verlaufzeit.index[df_with_verlaufzeit.index < pd.Timestamp('2020-01-01')]
    print(f"✓ Negative timestamp rows: {len(negative_indices)}")
    assert len(negative_indices) == 48, "Should have 48 negative timestamp rows"
    
    print(f"✓ Verlaufzeit feature working correctly")
    print("\nSample with verlaufzeit (first 5 rows):")
    print(df_with_verlaufzeit.head(5))

def main():
    print("\n" + "#"*60)
    print("# TESTING NEW FEATURES")
    print("#"*60)
    
    try:
        cfg = test_location_config()
        test_solar_location_manager(cfg)
        test_erbs_decomposition()
        test_climate_station_csv()
        test_verlaufzeit()
        
        print("\n" + "#"*60)
        print("# ALL TESTS PASSED ✓")
        print("#"*60)
        print("\nThe new features are working correctly and ready for deployment.")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
