import pytest
import pandas as pd
import numpy as np
import scipy.io as sio
import tempfile
from pathlib import Path
from core.storage.weather_repo import WeatherRepository


class TestWeatherRepository:
    """Test weather data handling for .mat, .csv, and .epw formats"""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for raw and processed weather data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_dir = Path(tmpdir) / "raw"
            processed_dir = Path(tmpdir) / "processed"
            raw_dir.mkdir(parents=True, exist_ok=True)
            processed_dir.mkdir(parents=True, exist_ok=True)
            yield raw_dir, processed_dir

    @pytest.fixture
    def sample_weather_data(self):
        """Create sample weather data (10 columns, 24 hours)"""
        data = {
            'timestamp': np.arange(24),
            'air_temperature': np.random.uniform(5, 25, 24),
            'relative_humidity': np.random.uniform(30, 90, 24),
            'wind_speed_x': np.random.uniform(0, 5, 24),
            'wind_speed_y': np.random.uniform(0, 5, 24),
            'solar_radiation_direct': np.random.uniform(0, 800, 24),
            'solar_radiation_diffuse': np.random.uniform(0, 200, 24),
            'sky_cover': np.random.uniform(0, 100, 24),
            'sun_elevation': np.random.uniform(-20, 80, 24),
            'sun_azimuth': np.random.uniform(0, 360, 24),
        }
        return data

    def test_read_raw_mat(self, temp_dirs, sample_weather_data):
        """Test reading .mat weather files"""
        raw_dir, processed_dir = temp_dirs
        mat_path = raw_dir / "weather.mat"

        # Create sample .mat file
        mat_data = {col: np.array([sample_weather_data[col]]) for col in sample_weather_data}
        sio.savemat(mat_path, mat_data)

        # Create repository and read
        repo = WeatherRepository(mat_path, processed_dir / "weather.parquet")
        result = repo.read_raw_mat()

        # Validate
        assert result is not None
        assert 'timestamp' in result or any(not k.startswith('__') for k in result.keys())
        print("✓ .mat file reading works")

    def test_read_raw_csv(self, temp_dirs, sample_weather_data):
        """Test reading .csv weather files"""
        raw_dir, processed_dir = temp_dirs
        csv_path = raw_dir / "weather.csv"

        # Create sample .csv file
        df = pd.DataFrame(sample_weather_data)
        df.to_csv(csv_path, index=False)

        # Create repository and read
        repo = WeatherRepository(csv_path, processed_dir / "weather.parquet")
        result = repo.read_raw_csv()

        # Validate
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 24
        assert list(result.columns) == list(sample_weather_data.keys())
        print("✓ .csv file reading works")

    def test_read_raw_epw(self, temp_dirs, sample_weather_data):
        """Test reading .epw weather files"""
        raw_dir, processed_dir = temp_dirs
        epw_path = raw_dir / "weather.epw"

        # Create sample .epw file with 8-line header and 35 columns
        with open(epw_path, 'w') as f:
            # Write 8 header lines
            for i in range(8):
                f.write(f"HEADER_LINE_{i+1}\n")
            # Write data: 10 required columns + 25 dummy columns = 35 total
            for i in range(24):
                row_data = [
                    2024, 1, 1, i, 0,  # Location/Date/Time (5 cols)
                    sample_weather_data['air_temperature'][i],  # col 6: Dry Bulb Temp
                    15.0,  # col 7: Dew Point
                    sample_weather_data['relative_humidity'][i],  # col 8: Relative Humidity
                    sample_weather_data['solar_radiation_direct'][i],  # col 9: Direct Normal Irrad
                    sample_weather_data['solar_radiation_diffuse'][i],  # col 10: Diffuse Horiz Irrad
                    100,  # col 11: Global Horiz Irrad
                    0,  # col 12-18: more dummy values
                    0, 0, 0, 0, 0, 0,
                    sample_weather_data['wind_speed_x'][i] + sample_weather_data['wind_speed_y'][i],  # col 20: Wind Speed
                    180,  # col 21: Wind Direction
                    0,  # col 22: Opaque Sky Cover
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  # col 23-35: remaining columns
                ]
                f.write(','.join(map(str, row_data)) + '\n')

        # Create repository and read
        repo = WeatherRepository(epw_path, processed_dir / "weather.parquet")
        result = repo.read_raw_epw()

        # Validate
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 24
        assert len(result.columns) == 35
        print("✓ .epw file reading works")

    def test_read_raw_auto_detect_mat(self, temp_dirs, sample_weather_data):
        """Test auto-detection for .mat format"""
        raw_dir, processed_dir = temp_dirs
        mat_path = raw_dir / "weather.mat"

        # Create sample .mat file
        mat_data = {col: np.array([sample_weather_data[col]]) for col in sample_weather_data}
        sio.savemat(mat_path, mat_data)

        # Create repository and use auto-detect
        repo = WeatherRepository(mat_path, processed_dir / "weather.parquet")
        result = repo.read_raw()

        # Validate
        assert result is not None
        print("✓ Auto-detection for .mat works")

    def test_read_raw_auto_detect_csv(self, temp_dirs, sample_weather_data):
        """Test auto-detection for .csv format"""
        raw_dir, processed_dir = temp_dirs
        csv_path = raw_dir / "weather.csv"

        # Create sample .csv file
        df = pd.DataFrame(sample_weather_data)
        df.to_csv(csv_path, index=False)

        # Create repository and use auto-detect
        repo = WeatherRepository(csv_path, processed_dir / "weather.parquet")
        result = repo.read_raw()

        # Validate
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 24
        print("✓ Auto-detection for .csv works")

    def test_read_raw_auto_detect_epw(self, temp_dirs, sample_weather_data):
        """Test auto-detection for .epw format"""
        raw_dir, processed_dir = temp_dirs
        epw_path = raw_dir / "weather.epw"

        # Create sample .epw file
        with open(epw_path, 'w') as f:
            for i in range(8):
                f.write(f"HEADER_LINE_{i+1}\n")
            for i in range(24):
                row_data = [2024, 1, 1, i, 0] + [0] * 30
                f.write(','.join(map(str, row_data)) + '\n')

        # Create repository and use auto-detect
        repo = WeatherRepository(epw_path, processed_dir / "weather.parquet")
        result = repo.read_raw()

        # Validate
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 24
        print("✓ Auto-detection for .epw works")

    def test_read_raw_unsupported_format(self, temp_dirs):
        """Test error handling for unsupported file format"""
        raw_dir, processed_dir = temp_dirs
        unsupported_path = raw_dir / "weather.txt"
        unsupported_path.write_text("dummy data")

        repo = WeatherRepository(unsupported_path, processed_dir / "weather.parquet")
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            repo.read_raw()
        
        print("✓ Error handling for unsupported formats works")

    def test_read_raw_file_not_found(self, temp_dirs):
        """Test handling of missing files"""
        raw_dir, processed_dir = temp_dirs
        missing_path = raw_dir / "missing_weather.csv"

        repo = WeatherRepository(missing_path, processed_dir / "weather.parquet")
        result = repo.read_raw()

        assert result is None
        print("✓ Handling of missing files works")

    def test_write_and_read_processed(self, temp_dirs, sample_weather_data):
        """Test writing and reading processed weather data (parquet)"""
        raw_dir, processed_dir = temp_dirs
        parquet_path = processed_dir / "weather.parquet"

        repo = WeatherRepository(raw_dir / "weather.csv", parquet_path)

        # Create sample processed data
        df = pd.DataFrame(sample_weather_data)
        df['datetime'] = pd.date_range('2024-01-01', periods=24, freq='h')
        df = df.set_index('datetime')

        # Write processed data
        repo.write_processed(df)

        # Read it back
        result = repo.read_processed()

        # Validate
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 24
        assert all(col in result.columns for col in sample_weather_data.keys())
        print("✓ Writing and reading processed data works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
