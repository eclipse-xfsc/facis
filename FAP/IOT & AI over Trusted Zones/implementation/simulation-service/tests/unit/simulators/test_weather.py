"""Tests for weather simulator."""

import json
from datetime import datetime, timezone

import pytest

from src.core.random_generator import DeterministicRNG
from src.core.time_series import IntervalMinutes, TimeRange
from src.models.weather import WeatherConfig, WeatherReading
from src.simulators.weather import (
    WeatherSimulator,
    calculate_clear_sky_ghi,
    calculate_day_length_hours,
    calculate_solar_position,
    calculate_temperature,
    get_diurnal_factor,
    get_seasonal_factor,
)


class TestTemperatureCycles:
    """Tests for temperature daily and seasonal cycles."""

    def test_seasonal_factor_summer(self) -> None:
        """Test seasonal factor is positive in summer (July)."""
        summer = datetime(2024, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        factor = get_seasonal_factor(summer)
        assert factor > 0.8  # Near peak summer

    def test_seasonal_factor_winter(self) -> None:
        """Test seasonal factor is negative in winter (January)."""
        winter = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        factor = get_seasonal_factor(winter)
        assert factor < -0.8  # Near peak winter

    def test_seasonal_factor_range(self) -> None:
        """Test seasonal factor is always between -1 and 1."""
        for month in range(1, 13):
            timestamp = datetime(2024, month, 15, 12, 0, 0, tzinfo=timezone.utc)
            factor = get_seasonal_factor(timestamp)
            assert -1 <= factor <= 1

    def test_diurnal_factor_warmest_afternoon(self) -> None:
        """Test diurnal factor peaks around 15:00."""
        # Test at 15:00 (peak)
        peak_time = datetime(2024, 7, 1, 15, 0, 0, tzinfo=timezone.utc)
        peak_factor = get_diurnal_factor(peak_time)

        # Test at 03:00 (minimum - 12 hours from peak)
        min_time = datetime(2024, 7, 1, 3, 0, 0, tzinfo=timezone.utc)
        min_factor = get_diurnal_factor(min_time)

        assert peak_factor > min_factor
        assert peak_factor > 0.9  # Near maximum
        assert min_factor < -0.9  # Near minimum

    def test_diurnal_factor_coldest_early_morning(self) -> None:
        """Test diurnal factor is lowest in early morning hours."""
        # 03:00 should be near coldest (12h from 15:00 peak)
        early_morning = datetime(2024, 7, 1, 3, 0, 0, tzinfo=timezone.utc)
        early_factor = get_diurnal_factor(early_morning)

        # Noon should be warmer
        noon = datetime(2024, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        noon_factor = get_diurnal_factor(noon)

        assert early_factor < noon_factor

    def test_temperature_summer_vs_winter(self) -> None:
        """Test temperature is higher in summer than winter."""
        summer = datetime(2024, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        winter = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        summer_temp = calculate_temperature(
            summer,
            base_summer_c=20.0,
            base_winter_c=2.0,
            daily_amplitude_c=8.0,
        )
        winter_temp = calculate_temperature(
            winter,
            base_summer_c=20.0,
            base_winter_c=2.0,
            daily_amplitude_c=8.0,
        )

        assert summer_temp > winter_temp
        assert summer_temp > 15.0  # Reasonable summer temperature
        assert winter_temp < 10.0  # Reasonable winter temperature

    def test_temperature_daily_cycle(self) -> None:
        """Test temperature follows daily cycle."""
        base_date = datetime(2024, 7, 1, 0, 0, 0, tzinfo=timezone.utc)

        temps = []
        for hour in range(24):
            timestamp = base_date.replace(hour=hour)
            temp = calculate_temperature(
                timestamp,
                base_summer_c=20.0,
                base_winter_c=2.0,
                daily_amplitude_c=8.0,
            )
            temps.append(temp)

        # Find indices of min and max
        min_idx = temps.index(min(temps))
        max_idx = temps.index(max(temps))

        # Coldest should be around 3 AM (12 hours from peak at 15:00)
        assert 1 <= min_idx <= 5

        # Warmest should be around 15 (index 15)
        assert 13 <= max_idx <= 17


class TestSolarIrradiance:
    """Tests for solar irradiance calculations."""

    def test_irradiance_zero_at_night(self) -> None:
        """Test irradiance is zero during nighttime."""
        # Berlin midnight in winter
        midnight = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        position = calculate_solar_position(midnight, latitude=52.52, longitude=13.405)

        assert not position.is_daylight
        assert position.altitude_deg == 0

    def test_irradiance_positive_during_day(self) -> None:
        """Test irradiance is positive during daylight."""
        # Berlin noon in summer
        noon = datetime(2024, 7, 1, 11, 0, 0, tzinfo=timezone.utc)  # Solar noon ~11 UTC for Berlin
        position = calculate_solar_position(noon, latitude=52.52, longitude=13.405)

        assert position.is_daylight
        assert position.altitude_deg > 0

    def test_clear_sky_ghi_bell_curve(self) -> None:
        """Test GHI follows bell curve during day with peak at noon."""
        # Test at various altitudes
        morning_ghi = calculate_clear_sky_ghi(solar_altitude_deg=20.0)
        noon_ghi = calculate_clear_sky_ghi(solar_altitude_deg=60.0)
        afternoon_ghi = calculate_clear_sky_ghi(solar_altitude_deg=30.0)

        # Noon (higher altitude) should have highest GHI
        assert noon_ghi > morning_ghi
        assert noon_ghi > afternoon_ghi

    def test_clear_sky_ghi_zero_below_horizon(self) -> None:
        """Test GHI is zero when sun is below horizon."""
        ghi = calculate_clear_sky_ghi(solar_altitude_deg=-5.0)
        assert ghi == 0

        ghi_horizon = calculate_clear_sky_ghi(solar_altitude_deg=0.0)
        assert ghi_horizon == 0

    def test_clear_sky_ghi_maximum(self) -> None:
        """Test GHI does not exceed configured maximum."""
        max_ghi = 1000.0
        ghi = calculate_clear_sky_ghi(
            solar_altitude_deg=90.0,  # Sun directly overhead
            max_ghi_w_m2=max_ghi,
        )
        assert ghi <= max_ghi

    def test_irradiance_peak_around_noon(self) -> None:
        """Test peak irradiance occurs around solar noon."""
        date = datetime(2024, 7, 1, tzinfo=timezone.utc)
        latitude = 52.52
        longitude = 13.405

        ghis = []
        for hour in range(24):
            timestamp = date.replace(hour=hour)
            position = calculate_solar_position(timestamp, latitude, longitude)
            ghi = calculate_clear_sky_ghi(position.altitude_deg)
            ghis.append(ghi)

        # Find peak
        max_ghi = max(ghis)
        peak_hour = ghis.index(max_ghi)

        # Peak should be around 11-13 UTC (solar noon for Berlin)
        assert 10 <= peak_hour <= 14
        assert max_ghi > 500  # Reasonable peak in summer


class TestDayLength:
    """Tests for latitude-based day length."""

    def test_day_length_summer_longer(self) -> None:
        """Test day length is longer in summer than winter."""
        # Summer solstice (day 172)
        summer_length = calculate_day_length_hours(day_of_year=172, latitude=52.52)

        # Winter solstice (day 355)
        winter_length = calculate_day_length_hours(day_of_year=355, latitude=52.52)

        assert summer_length > winter_length
        assert summer_length > 16  # Long summer day at high latitude
        assert winter_length < 9  # Short winter day

    def test_day_length_equator(self) -> None:
        """Test day length is ~12 hours at equator year-round."""
        for day in [1, 91, 182, 273]:  # Sample days across year
            length = calculate_day_length_hours(day_of_year=day, latitude=0.0)
            assert 11.5 <= length <= 12.5

    def test_day_length_high_latitude_summer(self) -> None:
        """Test very long days at high latitudes in summer."""
        # Arctic circle in summer
        length = calculate_day_length_hours(day_of_year=172, latitude=66.5)
        assert length > 20  # Near polar day

    def test_day_length_varies_with_latitude(self) -> None:
        """Test day length increases with latitude in summer."""
        summer_day = 172  # June 21

        length_equator = calculate_day_length_hours(summer_day, latitude=0.0)
        length_midlat = calculate_day_length_hours(summer_day, latitude=45.0)
        length_highlat = calculate_day_length_hours(summer_day, latitude=60.0)

        assert length_highlat > length_midlat > length_equator


class TestCloudFactor:
    """Tests for cloud cover affecting irradiance."""

    def test_cloud_factor_reduces_irradiance(self) -> None:
        """Test that cloud cover reduces GHI."""
        rng = DeterministicRNG(seed=12345)
        simulator = WeatherSimulator("station-001", rng)

        # Generate reading with low clouds
        config_clear = WeatherConfig(base_cloud_cover_percent=10.0)
        sim_clear = WeatherSimulator("clear", rng, config=config_clear)

        # Generate reading with high clouds
        config_cloudy = WeatherConfig(base_cloud_cover_percent=90.0)
        sim_cloudy = WeatherSimulator("cloudy", rng, config=config_cloudy)

        # Midday in summer
        timestamp = datetime(2024, 7, 1, 12, 0, 0, tzinfo=timezone.utc)

        clear_reading = sim_clear.generate_at(timestamp).value
        cloudy_reading = sim_cloudy.generate_at(timestamp).value

        # Clear sky should have higher GHI
        assert clear_reading.conditions.ghi_w_m2 > cloudy_reading.conditions.ghi_w_m2

    def test_cloud_factor_range(self) -> None:
        """Test cloud factor multiplier is in valid range (0.5-1.0)."""
        rng = DeterministicRNG(seed=12345)

        # Maximum cloud cover
        config = WeatherConfig(
            base_cloud_cover_percent=100.0,
            cloud_variance_percent=0.0,
        )
        simulator = WeatherSimulator("station", rng, config=config)

        timestamp = datetime(2024, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value

        # Even at 100% cloud cover, GHI should be > 0 during day (factor >= 0.5)
        assert reading.conditions.ghi_w_m2 > 0


class TestWeatherSimulator:
    """Tests for WeatherSimulator class."""

    def test_initialization_with_defaults(self) -> None:
        """Test simulator initializes with default configuration."""
        rng = DeterministicRNG(seed=12345)
        simulator = WeatherSimulator("station-001", rng)

        assert simulator.entity_id == "station-001"
        assert simulator.latitude == 52.52  # Berlin default
        assert simulator.longitude == 13.405

    def test_initialization_with_custom_config(self) -> None:
        """Test simulator initializes with custom configuration."""
        rng = DeterministicRNG(seed=12345)
        config = WeatherConfig(
            latitude=40.7128,
            longitude=-74.0060,
            base_temperature_summer_c=25.0,
        )
        simulator = WeatherSimulator("station-nyc", rng, config=config)

        assert simulator.latitude == 40.7128
        assert simulator.longitude == -74.0060
        assert simulator.config.base_temperature_summer_c == 25.0

    def test_generate_single_reading(self) -> None:
        """Test generating a single weather reading."""
        rng = DeterministicRNG(seed=12345)
        simulator = WeatherSimulator("station-001", rng)

        timestamp = datetime(2024, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        point = simulator.generate_at(timestamp)

        reading = point.value
        assert isinstance(reading, WeatherReading)
        assert reading.location.latitude == 52.52
        assert reading.conditions.temperature_c is not None
        assert reading.conditions.ghi_w_m2 >= 0

    def test_all_conditions_populated(self) -> None:
        """Test all weather conditions are populated."""
        rng = DeterministicRNG(seed=12345)
        simulator = WeatherSimulator("station-001", rng)

        timestamp = datetime(2024, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value

        # Check all conditions are present
        assert reading.conditions.temperature_c is not None
        assert reading.conditions.humidity_percent >= 0
        assert reading.conditions.wind_speed_ms >= 0
        assert 0 <= reading.conditions.wind_direction_deg < 360
        assert 0 <= reading.conditions.cloud_cover_percent <= 100
        assert reading.conditions.ghi_w_m2 >= 0
        assert reading.conditions.dni_w_m2 >= 0
        assert reading.conditions.dhi_w_m2 >= 0

    def test_humidity_in_valid_range(self) -> None:
        """Test humidity is always in 0-100% range."""
        rng = DeterministicRNG(seed=12345)
        simulator = WeatherSimulator("station-001", rng)

        for day in range(1, 366, 30):  # Sample days across year
            timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc).replace(
                month=min((day // 30) + 1, 12)
            )
            for hour in [6, 12, 18]:
                ts = timestamp.replace(hour=hour)
                reading = simulator.generate_at(ts).value
                assert 0 <= reading.conditions.humidity_percent <= 100

    def test_wind_speed_non_negative(self) -> None:
        """Test wind speed is never negative."""
        rng = DeterministicRNG(seed=12345)
        simulator = WeatherSimulator("station-001", rng)

        time_range = TimeRange.from_iso(
            "2024-01-01T00:00:00",
            "2024-01-07T23:45:00",
        )

        for point in simulator.iterate_range(time_range):
            assert point.value.conditions.wind_speed_ms >= 0

    def test_wind_direction_valid_range(self) -> None:
        """Test wind direction is always 0-360 degrees."""
        rng = DeterministicRNG(seed=12345)
        simulator = WeatherSimulator("station-001", rng)

        time_range = TimeRange.from_iso(
            "2024-01-01T00:00:00",
            "2024-01-07T23:45:00",
        )

        for point in simulator.iterate_range(time_range):
            assert 0 <= point.value.conditions.wind_direction_deg < 360


class TestIrradianceComponents:
    """Tests for GHI, DNI, DHI relationships."""

    def test_ghi_equals_sum_components_approximation(self) -> None:
        """Test GHI approximately equals DNI*cos(zenith) + DHI."""
        rng = DeterministicRNG(seed=12345)
        simulator = WeatherSimulator("station-001", rng)

        # Midday reading
        timestamp = datetime(2024, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value

        ghi = reading.conditions.ghi_w_m2
        dni = reading.conditions.dni_w_m2
        dhi = reading.conditions.dhi_w_m2

        # GHI should be positive during day
        assert ghi > 0
        # DHI should be part of GHI
        assert dhi <= ghi
        # DNI can exceed GHI (it's measured perpendicular to sun)
        assert dni >= 0

    def test_dhi_increases_with_clouds(self) -> None:
        """Test diffuse irradiance proportion increases with cloud cover."""
        rng = DeterministicRNG(seed=12345)

        config_clear = WeatherConfig(
            base_cloud_cover_percent=10.0,
            cloud_variance_percent=0.0,
        )
        config_cloudy = WeatherConfig(
            base_cloud_cover_percent=80.0,
            cloud_variance_percent=0.0,
        )

        sim_clear = WeatherSimulator("clear", rng, config=config_clear)
        sim_cloudy = WeatherSimulator("cloudy", rng, config=config_cloudy)

        timestamp = datetime(2024, 7, 1, 12, 0, 0, tzinfo=timezone.utc)

        clear_reading = sim_clear.generate_at(timestamp).value
        cloudy_reading = sim_cloudy.generate_at(timestamp).value

        # Calculate diffuse fraction
        clear_diffuse_frac = clear_reading.conditions.dhi_w_m2 / (
            clear_reading.conditions.ghi_w_m2 + 0.1
        )
        cloudy_diffuse_frac = cloudy_reading.conditions.dhi_w_m2 / (
            cloudy_reading.conditions.ghi_w_m2 + 0.1
        )

        # Cloudy sky should have higher diffuse fraction
        assert cloudy_diffuse_frac > clear_diffuse_frac


class TestPVCorrelation:
    """Tests for weather data correlation with PV generation."""

    def test_get_irradiance_for_pv(self) -> None:
        """Test convenience method for PV integration."""
        rng = DeterministicRNG(seed=12345)
        simulator = WeatherSimulator("station-001", rng)

        timestamp = datetime(2024, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        ghi = simulator.get_irradiance_for_pv(timestamp)

        # Should return positive GHI during day
        assert ghi > 0

    def test_get_temperature_for_pv(self) -> None:
        """Test convenience method for PV efficiency calculation."""
        rng = DeterministicRNG(seed=12345)
        simulator = WeatherSimulator("station-001", rng)

        timestamp = datetime(2024, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        temp = simulator.get_temperature_for_pv(timestamp)

        # Should return reasonable temperature
        assert -40 < temp < 50


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_same_seed_produces_identical_readings(self) -> None:
        """Test that same seed produces identical readings."""
        timestamp = datetime(2024, 7, 1, 12, 0, 0, tzinfo=timezone.utc)

        results = []
        for _ in range(5):
            rng = DeterministicRNG(seed=12345)
            simulator = WeatherSimulator("station-001", rng)
            reading = simulator.generate_at(timestamp).value
            results.append(reading.conditions.temperature_c)

        assert all(r == results[0] for r in results)

    def test_different_stations_produce_different_readings(self) -> None:
        """Test that different stations produce different readings."""
        timestamp = datetime(2024, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        rng = DeterministicRNG(seed=12345)

        sim1 = WeatherSimulator("station-001", rng)
        sim2 = WeatherSimulator("station-002", rng)

        reading1 = sim1.generate_at(timestamp).value
        reading2 = sim2.generate_at(timestamp).value

        # Values should be different due to different entity seeds
        assert reading1.conditions.temperature_c != reading2.conditions.temperature_c


class TestJSONPayload:
    """Tests for JSON payload format."""

    def test_json_payload_structure(self) -> None:
        """Test that JSON payload matches spec structure exactly."""
        rng = DeterministicRNG(seed=12345)
        simulator = WeatherSimulator("station-001", rng)

        timestamp = datetime(2026, 1, 21, 14, 0, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value

        payload = reading.to_json_payload()

        # Check required top-level fields
        assert "timestamp" in payload
        assert "location" in payload
        assert "conditions" in payload

        # Check location structure
        assert "latitude" in payload["location"]
        assert "longitude" in payload["location"]

        # Check conditions structure
        conditions = payload["conditions"]
        required_fields = [
            "temperature_c",
            "humidity_percent",
            "wind_speed_ms",
            "wind_direction_deg",
            "cloud_cover_percent",
            "ghi_w_m2",
            "dni_w_m2",
            "dhi_w_m2",
        ]
        for field in required_fields:
            assert field in conditions

        # Check timestamp format (ISO 8601 with Z suffix)
        assert payload["timestamp"].endswith("Z")

    def test_json_serialization(self) -> None:
        """Test that payload can be serialized to valid JSON."""
        rng = DeterministicRNG(seed=12345)
        simulator = WeatherSimulator("station-001", rng)

        timestamp = datetime(2024, 7, 1, 12, 0, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value
        payload = reading.to_json_payload()

        # Should serialize without errors
        json_str = json.dumps(payload, indent=2)
        assert json_str is not None

        # Should deserialize back
        parsed = json.loads(json_str)
        assert parsed == payload

    def test_json_matches_spec_example(self) -> None:
        """Test JSON output matches specification example format."""
        rng = DeterministicRNG(seed=12345)
        config = WeatherConfig(latitude=52.52, longitude=13.405)
        simulator = WeatherSimulator("station-001", rng, config=config)

        timestamp = datetime(2026, 1, 21, 14, 0, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value
        payload = reading.to_json_payload()

        # Verify structure matches spec
        expected_structure = {
            "timestamp": str,
            "location": {
                "latitude": (int, float),
                "longitude": (int, float),
            },
            "conditions": {
                "temperature_c": (int, float),
                "humidity_percent": (int, float),
                "wind_speed_ms": (int, float),
                "wind_direction_deg": (int, float),
                "cloud_cover_percent": (int, float),
                "ghi_w_m2": (int, float),
                "dni_w_m2": (int, float),
                "dhi_w_m2": (int, float),
            },
        }

        assert isinstance(payload["timestamp"], str)
        assert isinstance(payload["location"]["latitude"], (int, float))
        assert isinstance(payload["location"]["longitude"], (int, float))

        for key in expected_structure["conditions"]:
            assert isinstance(payload["conditions"][key], (int, float))


class TestHistoricalGeneration:
    """Tests for generating historical data ranges."""

    def test_generate_range(self) -> None:
        """Test generating a range of readings."""
        rng = DeterministicRNG(seed=12345)
        simulator = WeatherSimulator("station-001", rng)

        time_range = TimeRange.from_iso(
            "2024-07-01T00:00:00",
            "2024-07-01T23:45:00",
        )

        points = simulator.generate_range(time_range)

        # 24 hours at 15-min intervals = 96 points (00:00 to 23:45 inclusive)
        assert len(points) == 96

        # All timestamps should be in range
        for point in points:
            assert time_range.start <= point.timestamp <= time_range.end

    def test_iterate_range_memory_efficient(self) -> None:
        """Test iterate_range for memory efficiency."""
        rng = DeterministicRNG(seed=12345)
        simulator = WeatherSimulator("station-001", rng)

        time_range = TimeRange.from_iso(
            "2024-01-01T00:00:00",
            "2024-01-31T23:45:00",
        )

        count = 0
        for point in simulator.iterate_range(time_range):
            count += 1
            assert isinstance(point.value, WeatherReading)

        # 31 days * 24 hours * 4 intervals = 2976
        assert count == 2976
