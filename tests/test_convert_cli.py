#!/usr/bin/env python
"""
Test the convert_climate_station.py CLI tool
"""
import subprocess
import sys
from pathlib import Path
import pandas as pd

def test_convert_cli():
    """Test the standalone converter CLI"""
    print("\n" + "="*60)
    print("TEST: convert_climate_station.py CLI Tool")
    print("="*60)
    
    # Input and output paths
    input_csv = Path('/home/gianl/Downloads/100254.csv')
    output_csv = Path('/tmp/weather_converted.csv')
    
    # Remove output if it exists
    if output_csv.exists():
        output_csv.unlink()
    
    if not input_csv.exists():
        print(f"✗ Input file not found: {input_csv}")
        return False
    
    print(f"✓ Input file found: {input_csv}")
    
    # Run the converter
    cmd = [
        sys.executable,
        'convert_climate_station.py',
        str(input_csv),
        str(output_csv),
        '--latitude', '47.5596',
        '--longitude', '7.5922'
    ]
    
    print(f"\nRunning: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            cwd='/home/gianl/Dokumente/projekte/VM2-RC-Modell-ui',
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"✗ Command failed with return code {result.returncode}")
            print(f"Error output:\n{result.stderr}")
            return False
        
        print("✓ Converter executed successfully")
        
        # Check output file
        if not output_csv.exists():
            print(f"✗ Output file not created: {output_csv}")
            return False
        
        print(f"✓ Output file created: {output_csv}")
        
        # Verify output format
        try:
            df = pd.read_csv(output_csv)
            print(f"✓ Output file is valid CSV")
            print(f"✓ Shape: {df.shape}")
            print(f"✓ Columns: {list(df.columns)}")
            
            # Check for required columns
            required_cols = [
                'timestamp', 'air_temperature', 'relative_humidity',
                'wind_speed_x', 'wind_speed_y', 'solar_radiation_direct',
                'solar_radiation_diffuse', 'sky_cover', 'sun_elevation', 'sun_azimuth'
            ]
            
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"✗ Missing columns: {missing_cols}")
                return False
            
            print(f"✓ All required columns present")
            print(f"\nFirst 5 rows:")
            print(df.head())
            
            print(f"\nData quality checks:")
            print(f"  - Temperature range: {df['air_temperature'].min():.1f}°C to {df['air_temperature'].max():.1f}°C")
            print(f"  - Humidity range: {df['relative_humidity'].min():.0f}% to {df['relative_humidity'].max():.0f}%")
            print(f"  - Global radiation (direct+diffuse) range: {(df['solar_radiation_direct'] + df['solar_radiation_diffuse']).min():.0f} to {(df['solar_radiation_direct'] + df['solar_radiation_diffuse']).max():.0f} W/m²")
            print(f"  - Sun elevation range: {df['sun_elevation'].min():.1f}° to {df['sun_elevation'].max():.1f}°")
            
            return True
            
        except Exception as e:
            print(f"✗ Error reading output CSV: {e}")
            return False
        
    except subprocess.TimeoutExpired:
        print(f"✗ Converter timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"✗ Error running converter: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# TESTING CLIMATE STATION CONVERTER")
    print("#"*60)
    
    success = test_convert_cli()
    
    if success:
        print("\n" + "#"*60)
        print("# CLI CONVERTER TEST PASSED ✓")
        print("#"*60)
        sys.exit(0)
    else:
        print("\n" + "#"*60)
        print("# CLI CONVERTER TEST FAILED ✗")
        print("#"*60)
        sys.exit(1)
