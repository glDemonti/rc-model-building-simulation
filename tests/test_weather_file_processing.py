"""
Tests for weather file processing: date handling, content verification, and column mapping.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.io import savemat
from core.weather_service import WeatherService
from core.storage.weather_repo import WeatherRepository


class TestWeatherFileProcessing:
    """Test suite for verifying weather file processing across different formats."""
    
    @pytest.fixture
    def temp_weather_dir(self, tmp_path):
        """Create temporary directories for weather files."""
        raw_dir = tmp_path / "raw"
        processed_dir = tmp_path / "processed"
        raw_dir.mkdir()
        processed_dir.mkdir()
        return raw_dir, processed_dir
    
    def test_mat_file_datetime_parsing(self, temp_weather_dir):
        """Test that MAT files parse timestamp column correctly."""
        raw_dir, processed_dir = temp_weather_dir
        
        # Create MAT file with datetime timestamps
        timestamps = pd.date_range("2019-01-01 00:00:00", periods=168, freq='h')
        weather_data = np.column_stack([
            timestamps.astype(np.int64) // 10**9,  # Unix timestamps
            np.random.uniform(15, 25, 168),  # air_temperature
            np.random.uniform(30, 70, 168),  # relative_humidity
            np.random.uniform(-2, 5, 168),   # wind_speed_x
            np.random.uniform(-2, 5, 168),   # wind_speed_y
            np.random.uniform(0, 800, 168),  # solar_radiation_direct
            np.random.uniform(0, 200, 168),  # solar_radiation_diffuse
            np.random.uniform(0, 100, 168),  # sky_cover
            np.random.uniform(0, 90, 168),   # sun_elevation
            np.random.uniform(0, 360, 168),  # sun_azimuth
        ])
        
        mat_file = raw_dir / "weather.mat"
        savemat(str(mat_file), {"weather_table": weather_data})
        
        # Create repository and service
        repo = WeatherRepository(mat_file, processed_dir / "weather.parquet")
        service = WeatherService(repo)
        
        # Process the file
        df = service.process_and_store_weather()
        
        # Verify datetime index
        assert isinstance(df.index, pd.DatetimeIndex)
        assert len(df) == 168
        
        # Verify columns are present and timestamp is removed
        expected_columns = [
            'air_temperature', 'relative_humidity', 'wind_speed_x', 'wind_speed_y',
            'solar_radiation_direct', 'solar_radiation_diffuse', 'sky_cover',
            'sun_elevation', 'sun_azimuth'
        ]
        assert list(df.columns) == expected_columns
        assert 'timestamp' not in df.columns
    
    def test_csv_file_datetime_parsing(self, temp_weather_dir):
        """Test that CSV files parse timestamp column correctly."""
        raw_dir, processed_dir = temp_weather_dir
        
        # Create CSV with datetime strings
        timestamps = pd.date_range("2019-06-15 00:00:00", periods=100, freq='h')
        csv_data = pd.DataFrame({
            'timestamp': timestamps.strftime('%Y-%m-%d %H:%M:%S'),
            'air_temperature': np.random.uniform(20, 30, 100),
            'relative_humidity': np.random.uniform(40, 80, 100),
            'wind_speed_x': np.random.uniform(-3, 3, 100),
            'wind_speed_y': np.random.uniform(-3, 3, 100),
            'solar_radiation_direct': np.random.uniform(0, 1000, 100),
            'solar_radiation_diffuse': np.random.uniform(0, 300, 100),
            'sky_cover': np.random.uniform(0, 100, 100),
            'sun_elevation': np.random.uniform(0, 90, 100),
            'sun_azimuth': np.random.uniform(0, 360, 100),
        })
        
        csv_file = raw_dir / "weather.csv"
        csv_data.to_csv(csv_file, index=False)
        
        repo = WeatherRepository(csv_file, processed_dir / "weather.parquet")
        service = WeatherService(repo)
        
        df = service.process_and_store_weather()
        
        # Verify datetime parsing
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.index.min() == pd.Timestamp("2019-06-15 00:00:00")
        assert len(df) == 100
        
        # Verify columns
        expected_columns = [
            'air_temperature', 'relative_humidity', 'wind_speed_x', 'wind_speed_y',
            'solar_radiation_direct', 'solar_radiation_diffuse', 'sky_cover',
            'sun_elevation', 'sun_azimuth'
        ]
        assert list(df.columns) == expected_columns
        assert 'timestamp' not in df.columns
    
    def test_epw_file_uses_config_start_date(self, temp_weather_dir):
        """Test that EPW files use configurable start_date from config."""
        raw_dir, processed_dir = temp_weather_dir
        
        # Create minimal EPW file (8760 hours for full year)
        epw_data = []
        for month in range(1, 13):
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1]
            for day in range(1, days_in_month + 1):
                for hour in range(1, 25):
                    epw_data.append([
                        1999, month, day, hour,  # Year, Month, Day, Hour
                        60,  # Minute
                        0, 0, 0, 0, 0, 0, 0, 0,  # Data source flags
                        20.0,  # Dry Bulb Temperature
                        15.0,  # Dew Point Temperature
                        75.0,  # Relative Humidity
                        101325,  # Atmospheric Pressure
                        0, 0,  # Extraterrestrial radiation
                        0, 0, 0,  # IR radiation
                        0, 0, 0,  # Sky cover
                        10000,  # Visibility
                        0,  # Ceiling Height
                        0, 0, 0,  # Weather codes
                        0, 0,  # Precipitation
                        0, 0, 0,  # Snow
                        5.0,  # Wind Speed
                        180,  # Wind Direction
                    ])
        
        epw_df = pd.DataFrame(epw_data)
        epw_file = raw_dir / "weather.epw"
        
        # Write EPW with header lines
        with open(epw_file, 'w') as f:
            f.write("LOCATION,Test,Country,Source,TMY3,999999,0.0,0.0,0.0,0.0\n")
            f.write("DESIGN CONDITIONS,0\n")
            f.write("TYPICAL/EXTREME PERIODS,0\n")
            f.write("GROUND TEMPERATURES,0\n")
            f.write("HOLIDAYS/DAYLIGHT SAVINGS,No,0,0,0\n")
            f.write("COMMENTS 1,\n")
            f.write("COMMENTS 2,\n")
            f.write("DATA PERIODS,1,1,Data,Sunday,1/1,12/31\n")
        epw_df.to_csv(epw_file, mode='a', header=False, index=False)
        
        repo = WeatherRepository(epw_file, processed_dir / "weather.parquet")
        service = WeatherService(repo)
        
        # Config with custom start date
        cfg = {
            "simulation_parameters": {
                "weather_start_date": {
                    "value": "2020-03-15 00:00:00"
                }
            }
        }
        
        df = service.process_and_store_weather(cfg)
        
        # Verify EPW uses config start_date (not file year 1999)
        assert df.index.min() == pd.Timestamp("2020-03-15 00:00:00")
        assert isinstance(df.index, pd.DatetimeIndex)
        assert len(df) == 8760
    
    def test_epw_requires_config(self, temp_weather_dir):
        """Test that EPW files raise error when no config provided."""
        raw_dir, processed_dir = temp_weather_dir
        
        # Create minimal EPW
        epw_file = raw_dir / "weather.epw"
        with open(epw_file, 'w') as f:
            f.write("LOCATION,Test,Country,Source,TMY3,999999,0.0,0.0,0.0,0.0\n")
            f.write("DESIGN CONDITIONS,0\n")
            f.write("TYPICAL/EXTREME PERIODS,0\n")
            f.write("GROUND TEMPERATURES,0\n")
            f.write("HOLIDAYS/DAYLIGHT SAVINGS,No,0,0,0\n")
            f.write("COMMENTS 1,\n")
            f.write("COMMENTS 2,\n")
            f.write("DATA PERIODS,1,1,Data,Sunday,1/1,12/31\n")
            # Just one data row for testing
            f.write("2023,1,1,1,60,0,0,0,0,0,0,0,0,20.0,15.0,75.0,101325,0,0,0,0,0,0,0,0,10000,0,0,0,0,0,0,0,0,0,5.0,180\n")
        
        repo = WeatherRepository(epw_file, processed_dir / "weather.parquet")
        service = WeatherService(repo)
        
        # Should raise error without config
        with pytest.raises(ValueError, match="EPW files require weather_start_date"):
            service.process_and_store_weather(cfg=None)
    
    def test_mat_column_content_integrity(self, temp_weather_dir):
        """Test that MAT file data values are preserved correctly."""
        raw_dir, processed_dir = temp_weather_dir
        
        # Create MAT with known values
        timestamps = pd.date_range("2019-01-01", periods=10, freq='h')
        expected_temp = [20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0, 24.5, 25.0]
        expected_humidity = [50, 51, 52, 53, 54, 55, 56, 57, 58, 59]
        
        weather_data = np.column_stack([
            timestamps.astype(np.int64) // 10**9,
            expected_temp,
            expected_humidity,
            np.zeros(10),  # wind_speed_x
            np.zeros(10),  # wind_speed_y
            np.ones(10) * 500,  # solar_radiation_direct
            np.ones(10) * 100,  # solar_radiation_diffuse
            np.ones(10) * 20,  # sky_cover
            np.ones(10) * 45,  # sun_elevation
            np.ones(10) * 180,  # sun_azimuth
        ])
        
        mat_file = raw_dir / "weather.mat"
        savemat(str(mat_file), {"weather_table": weather_data})
        
        repo = WeatherRepository(mat_file, processed_dir / "weather.parquet")
        service = WeatherService(repo)
        df = service.process_and_store_weather()
        
        # Verify data integrity
        np.testing.assert_array_almost_equal(df['air_temperature'].values, expected_temp)
        np.testing.assert_array_almost_equal(df['relative_humidity'].values, expected_humidity)
        np.testing.assert_array_almost_equal(df['solar_radiation_direct'].values, np.ones(10) * 500)
    
    def test_csv_extra_columns_ignored(self, temp_weather_dir):
        """Test that CSV files with extra columns only use first 10."""
        raw_dir, processed_dir = temp_weather_dir
        
        timestamps = pd.date_range("2019-01-01", periods=5, freq='h')
        csv_data = pd.DataFrame({
            'timestamp': timestamps.strftime('%Y-%m-%d %H:%M:%S'),
            'col1': [1, 2, 3, 4, 5],
            'col2': [1, 2, 3, 4, 5],
            'col3': [1, 2, 3, 4, 5],
            'col4': [1, 2, 3, 4, 5],
            'col5': [1, 2, 3, 4, 5],
            'col6': [1, 2, 3, 4, 5],
            'col7': [1, 2, 3, 4, 5],
            'col8': [1, 2, 3, 4, 5],
            'col9': [1, 2, 3, 4, 5],
            'extra_col1': [99, 99, 99, 99, 99],  # Should be ignored
            'extra_col2': [99, 99, 99, 99, 99],  # Should be ignored
        })
        
        csv_file = raw_dir / "weather.csv"
        csv_data.to_csv(csv_file, index=False)
        
        repo = WeatherRepository(csv_file, processed_dir / "weather.parquet")
        service = WeatherService(repo)
        df = service.process_and_store_weather()
        
        # Should only have 9 columns (10 - timestamp)
        assert len(df.columns) == 9
        assert 'extra_col1' not in df.columns

    def test_csv_semicolon_with_decimal_comma(self, temp_weather_dir):
        """Test semicolon-separated CSV with German decimal commas."""
        raw_dir, processed_dir = temp_weather_dir

        timestamps = pd.date_range("2019-01-01", periods=4, freq='h')
        csv_data = pd.DataFrame({
            'timestamp': timestamps.strftime('%Y-%m-%d %H:%M:%S'),
            'air_temperature': [20.5, 21.0, 21.5, 22.0],
            'relative_humidity': [50.0, 51.0, 52.0, 53.0],
            'wind_speed_x': [1.1, 1.2, 1.3, 1.4],
            'wind_speed_y': [0.1, 0.2, 0.3, 0.4],
            'solar_radiation_direct': [100.0, 110.0, 120.0, 130.0],
            'solar_radiation_diffuse': [30.0, 31.0, 32.0, 33.0],
            'sky_cover': [10.0, 11.0, 12.0, 13.0],
            'sun_elevation': [15.0, 20.0, 25.0, 30.0],
            'sun_azimuth': [90.0, 100.0, 110.0, 120.0],
        })

        csv_file = raw_dir / "weather_de.csv"
        csv_data.to_csv(csv_file, sep=';', decimal=',', index=False)

        repo = WeatherRepository(csv_file, processed_dir / "weather.parquet")
        service = WeatherService(repo)
        df = service.process_and_store_weather()

        assert isinstance(df.index, pd.DatetimeIndex)
        np.testing.assert_array_almost_equal(
            df['air_temperature'].values,
            [20.5, 21.0, 21.5, 22.0],
        )

    def test_mat_hour_counter_creates_hourly_datetime_index(
        self, temp_weather_dir
    ):
        """MAT hour counters like 1..N should map to hourly timeline."""
        raw_dir, processed_dir = temp_weather_dir

        hour_counter = np.arange(1, 25)
        weather_data = np.column_stack([
            hour_counter,
            np.random.uniform(15, 25, 24),
            np.random.uniform(30, 70, 24),
            np.random.uniform(-2, 5, 24),
            np.random.uniform(-2, 5, 24),
            np.random.uniform(0, 800, 24),
            np.random.uniform(0, 200, 24),
            np.random.uniform(0, 100, 24),
            np.random.uniform(0, 90, 24),
            np.random.uniform(0, 360, 24),
        ])

        mat_file = raw_dir / "weather_counter.mat"
        savemat(str(mat_file), {"weather_table": weather_data})

        repo = WeatherRepository(mat_file, processed_dir / "weather.parquet")
        service = WeatherService(repo)

        cfg = {
            "simulation_parameters": {
                "weather_start_date": {
                    "value": "2020-01-01 00:00:00"
                }
            }
        }

        df = service.process_and_store_weather(cfg)

        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.index[0] == pd.Timestamp("2020-01-01 00:00:00")
        assert df.index[1] - df.index[0] == pd.Timedelta(hours=1)
        assert 'extra_col2' not in df.columns
    
    def test_processed_file_persistence(self, temp_weather_dir):
        """Test that processed weather is saved and can be reloaded."""
        raw_dir, processed_dir = temp_weather_dir
        
        timestamps = pd.date_range("2019-01-01", periods=24, freq='h')
        csv_data = pd.DataFrame({
            'timestamp': timestamps.strftime('%Y-%m-%d %H:%M:%S'),
            'air_temperature': np.random.uniform(15, 25, 24),
            'relative_humidity': np.random.uniform(30, 70, 24),
            'wind_speed_x': np.random.uniform(-2, 5, 24),
            'wind_speed_y': np.random.uniform(-2, 5, 24),
            'solar_radiation_direct': np.random.uniform(0, 800, 24),
            'solar_radiation_diffuse': np.random.uniform(0, 200, 24),
            'sky_cover': np.random.uniform(0, 100, 24),
            'sun_elevation': np.random.uniform(0, 90, 24),
            'sun_azimuth': np.random.uniform(0, 360, 24),
        })
        
        csv_file = raw_dir / "weather.csv"
        csv_data.to_csv(csv_file, index=False)
        
        repo = WeatherRepository(csv_file, processed_dir / "weather.parquet")
        service = WeatherService(repo)
        
        # Process and store
        df_original = service.process_and_store_weather()
        
        # Reload from processed
        df_reloaded = service.load_weather()
        
        # Verify they match
        pd.testing.assert_frame_equal(df_original, df_reloaded)
        assert (processed_dir / "weather.parquet").exists()
