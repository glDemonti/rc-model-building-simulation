"""
Solar utilities for weather data processing.

Provides:
- Location-based solar position calculations
- Solar radiation decomposition (Erbs model)
- Flexible sun elevation and azimuth calculations for any location
"""

import numpy as np
import pandas as pd
from typing import Tuple


class SolarLocationManager:
    """Manages location coordinates for solar calculations."""
    
    # Default location (Basel, Switzerland) - for backward compatibility
    DEFAULT_LATITUDE = 47.5596
    DEFAULT_LONGITUDE = 7.5922
    
    def __init__(self, latitude: float = None, longitude: float = None):
        """
        Initialize location manager.
        
        Args:
            latitude: Location latitude in degrees (default: Basel)
            longitude: Location longitude in degrees (default: Basel)
        """
        self.latitude = latitude if latitude is not None else self.DEFAULT_LATITUDE
        self.longitude = longitude if longitude is not None else self.DEFAULT_LONGITUDE
    
    @staticmethod
    def from_config(cfg: dict) -> 'SolarLocationManager':
        """
        Create SolarLocationManager from configuration dictionary.
        
        Args:
            cfg: Configuration dict with optional 'location' section:
                {
                    "location": {
                        "latitude": {"expression": "47.5596", "value": 47.5596, ...},
                        "longitude": {"expression": "7.5922", "value": 7.5922, ...}
                    }
                }
        
        Returns:
            SolarLocationManager instance
        """
        location_cfg = cfg.get("location", {})
        
        # Extract values from nested config structure
        latitude = None
        if isinstance(location_cfg.get("latitude"), dict):
            latitude = location_cfg["latitude"].get("value")
        else:
            latitude = location_cfg.get("latitude")
            
        longitude = None
        if isinstance(location_cfg.get("longitude"), dict):
            longitude = location_cfg["longitude"].get("value")
        else:
            longitude = location_cfg.get("longitude")
        
        return SolarLocationManager(latitude=latitude, longitude=longitude)
    
    def get_coordinates(self) -> Tuple[float, float]:
        """Return (latitude, longitude) tuple."""
        return (self.latitude, self.longitude)


class SolarRadiationDecomposition:
    """Decompose global horizontal radiation into direct and diffuse components using Erbs model."""
    
    @staticmethod
    def decompose_global_radiation(
        global_radiation: np.ndarray,
        sun_elevation: np.ndarray,
        datetime_index: pd.DatetimeIndex = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Decompose global horizontal radiation (GHR) into direct and diffuse components.
        
        Uses Erbs et al. (1982) model with clearness index.
        Reference: Erbs, D. G., Klein, S. A., & Duffie, J. A. (1982).
        Estimation of diffuse radiation fraction for hourly, daily and monthly-average global radiation.
        
        Args:
            global_radiation: Global horizontal radiation [W/m²]
            sun_elevation: Solar elevation angles [degrees]
            datetime_index: DatetimeIndex for extraterrestrial radiation calculation (optional)
        
        Returns:
            Tuple of (direct_radiation, diffuse_radiation) in [W/m²]
        """
        # Ensure arrays
        ghr = np.asarray(global_radiation, dtype=float)
        elevation = np.asarray(sun_elevation, dtype=float)
        
        # Calculate extraterrestrial radiation (Angstrom extraterrestrial model)
        # This is the radiation at Earth's mean orbital distance before atmospheric effects
        extr_rad = SolarRadiationDecomposition._calculate_extraterrestrial_radiation(elevation)
        
        # Clearness index: ratio of ground to extraterrestrial radiation
        # Avoid division by zero
        kt = np.divide(ghr, extr_rad, where=extr_rad > 0, out=np.zeros_like(ghr, dtype=float))
        kt = np.clip(kt, 0, 1)  # Physical bounds
        
        # Erbs model: calculate diffuse fraction based on clearness index and sun elevation
        diffuse_fraction = SolarRadiationDecomposition._erbs_diffuse_fraction(kt, elevation)
        
        # Decompose into components
        diffuse = ghr * diffuse_fraction
        direct = ghr * (1 - diffuse_fraction)
        
        # Direct radiation cannot be negative; set to zero when sun is below horizon
        direct = np.maximum(direct, 0)
        
        return direct, diffuse
    
    @staticmethod
    def _calculate_extraterrestrial_radiation(sun_elevation: np.ndarray) -> np.ndarray:
        """
        Calculate extraterrestrial solar radiation (before atmospheric effects).
        
        Uses simplified model based on solar constant and sun elevation.
        
        Args:
            sun_elevation: Solar elevation angles [degrees]
        
        Returns:
            Extraterrestrial radiation [W/m²]
        """
        # Solar constant (W/m²)
        I_sc = 1367.0
        
        # Convert elevation to radians and clip negative values (sun below horizon)
        elevation_rad = np.radians(np.maximum(sun_elevation, 0))
        
        # Extraterrestrial on horizontal surface = I_sc * sin(elevation)
        # Use simplified atmosphericratio
        extr_rad = I_sc * np.sin(elevation_rad)
        
        return np.maximum(extr_rad, 0)
    
    @staticmethod
    def _erbs_diffuse_fraction(clearness_index: np.ndarray, sun_elevation: np.ndarray) -> np.ndarray:
        """
        Calculate diffuse fraction using Erbs et al. (1982) model.
        
        Args:
            clearness_index: Kt (GHR / Extraterrestrial radiation)
            sun_elevation: Solar elevation angles [degrees]
        
        Returns:
            Diffuse fraction (0 to 1)
        """
        # Sin of elevation angle (physical constraint: sun above/below horizon)
        sin_elevation = np.maximum(np.sin(np.radians(sun_elevation)), 0)
        
        # Initialize diffuse fraction array
        kd = np.zeros_like(clearness_index)
        
        # Three regions based on clearness index
        mask_low = clearness_index <= 0.22
        mask_mid = (clearness_index > 0.22) & (clearness_index <= 0.80)
        mask_high = clearness_index > 0.80
        
        # Low clearness (very cloudy)
        kd[mask_low] = (
            1.020 - 0.254 * clearness_index[mask_low] + 0.0123 * sin_elevation[mask_low]
        )
        
        # Medium clearness (partly cloudy)
        kd[mask_mid] = (
            0.506 - 0.461 * clearness_index[mask_mid] + 0.0694 * sin_elevation[mask_mid]
        )
        
        # High clearness (clear sky)
        kd[mask_high] = (
            0.210 - 0.295 * clearness_index[mask_high] + 0.0688 * sin_elevation[mask_high]
        )
        
        # Physical bounds: diffuse fraction must be between 0 and 1
        kd = np.clip(kd, 0, 1)
        
        return kd


class SolarPositionCalculator:
    """Calculate sun position (elevation and azimuth) for any location."""
    
    def __init__(self, latitude: float, longitude: float):
        """
        Initialize calculator for a specific location.
        
        Args:
            latitude: Location latitude in degrees
            longitude: Location longitude in degrees
        """
        self.latitude = latitude
        self.longitude = longitude
    
    def calculate_sun_elevation(self, datetimes: pd.DatetimeIndex) -> np.ndarray:
        """
        Calculate solar elevation angle using simplified solar position algorithm.
        
        Args:
            datetimes: Sequence of datetime values
        
        Returns:
            Array of sun elevation angles in degrees
        """
        dates = pd.DatetimeIndex(datetimes)
        day_of_year = dates.dayofyear.values
        
        # Declination angle (easy calculation)
        B = 360.0 * (day_of_year - 1) / 365.0
        B_rad = np.radians(B)
        declination = 23.45 * np.sin(B_rad)
        
        # Hour angle and time offset
        time_offset = dates.hour + dates.minute / 60.0
        hour_angle = 15.0 * (time_offset - 12.0) + (self.longitude - 15.0)
        
        # Solar elevation angle
        lat_rad = np.radians(self.latitude)
        decl_rad = np.radians(declination)
        hour_angle_rad = np.radians(hour_angle)
        
        sin_elev = (
            np.sin(lat_rad) * np.sin(decl_rad) +
            np.cos(lat_rad) * np.cos(decl_rad) * np.cos(hour_angle_rad)
        )
        elevation = np.degrees(np.arcsin(np.clip(sin_elev, -1, 1)))
        
        return elevation
    
    def calculate_sun_azimuth(self, datetimes: pd.DatetimeIndex) -> np.ndarray:
        """
        Calculate solar azimuth angle using simplified solar position algorithm.
        
        Args:
            datetimes: Sequence of datetime values
        
        Returns:
            Array of sun azimuth angles in degrees (0=North, 90=East, 180=South, 270=West)
        """
        dates = pd.DatetimeIndex(datetimes)
        day_of_year = dates.dayofyear.values
        
        # Declination angle
        B = 360.0 * (day_of_year - 1) / 365.0
        B_rad = np.radians(B)
        declination = 23.45 * np.sin(B_rad)
        
        # Hour angle and time offset
        time_offset = dates.hour + dates.minute / 60.0
        hour_angle = 15.0 * (time_offset - 12.0) + (self.longitude - 15.0)
        
        # Solar azimuth angle
        lat_rad = np.radians(self.latitude)
        decl_rad = np.radians(declination)
        hour_angle_rad = np.radians(hour_angle)
        
        # Azimuth calculation (0=North, increases clockwise)
        numerator = np.sin(hour_angle_rad)
        denominator = (
            np.sin(lat_rad) * np.cos(hour_angle_rad) -
            np.cos(lat_rad) * np.tan(decl_rad)
        )
        azimuth = np.degrees(np.arctan2(numerator, denominator))
        azimuth = (azimuth + 180) % 360  # Convert to 0-360 range
        
        return azimuth
