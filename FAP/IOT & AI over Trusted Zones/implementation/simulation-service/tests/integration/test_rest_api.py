"""Integration tests for REST API."""

import pytest
from fastapi.testclient import TestClient

from src.api.rest.app import create_app
from src.api.rest.dependencies import SimulationState


@pytest.fixture
def client():
    """Create a test client with fresh simulation state."""
    # Reset singleton state before each test
    SimulationState.reset_instance()

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    # Cleanup after test
    SimulationState.reset_instance()


class TestHealthEndpoints:
    """Tests for health and config endpoints."""

    def test_health_check(self, client: TestClient) -> None:
        """Test GET /api/v1/health returns healthy status."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "facis-simulation-service"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data

    def test_get_config(self, client: TestClient) -> None:
        """Test GET /api/v1/config returns configuration."""
        response = client.get("/api/v1/config")

        assert response.status_code == 200
        data = response.json()
        assert "seed" in data
        assert "time_acceleration" in data
        assert "simulation_state" in data
        assert "registered_meters" in data
        assert "registered_price_feeds" in data

    def test_update_config_seed(self, client: TestClient) -> None:
        """Test PUT /api/v1/config updates seed."""
        response = client.put("/api/v1/config", json={"seed": 99999})

        assert response.status_code == 200
        data = response.json()
        assert data["seed"] == 99999

    def test_update_config_acceleration(self, client: TestClient) -> None:
        """Test PUT /api/v1/config updates acceleration."""
        response = client.put("/api/v1/config", json={"time_acceleration": 100})

        assert response.status_code == 200
        data = response.json()
        assert data["time_acceleration"] == 100


class TestMeterEndpoints:
    """Tests for meter endpoints."""

    def test_list_meters(self, client: TestClient) -> None:
        """Test GET /api/v1/meters returns list of meters."""
        response = client.get("/api/v1/meters")

        assert response.status_code == 200
        data = response.json()
        assert "meters" in data
        assert "count" in data
        assert data["count"] >= 1
        assert len(data["meters"]) == data["count"]

    def test_get_meter_current(self, client: TestClient) -> None:
        """Test GET /api/v1/meters/{id}/current returns current reading."""
        response = client.get("/api/v1/meters/janitza-umg96rm-001/current")

        assert response.status_code == 200
        data = response.json()
        assert data["meter_id"] == "janitza-umg96rm-001"
        assert "timestamp" in data
        assert "readings" in data

        readings = data["readings"]
        assert "active_power_l1_w" in readings
        assert "voltage_l1_v" in readings
        assert "current_l1_a" in readings
        assert "power_factor" in readings
        assert "frequency_hz" in readings
        assert "total_energy_kwh" in readings

    def test_get_meter_current_not_found(self, client: TestClient) -> None:
        """Test GET /api/v1/meters/{id}/current returns 404 for unknown meter."""
        response = client.get("/api/v1/meters/unknown-meter/current")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_get_meter_history(self, client: TestClient) -> None:
        """Test GET /api/v1/meters/{id}/history returns historical readings."""
        response = client.get("/api/v1/meters/janitza-umg96rm-001/history")

        assert response.status_code == 200
        data = response.json()
        assert data["meter_id"] == "janitza-umg96rm-001"
        assert "readings" in data
        assert "count" in data
        assert "limit" in data
        assert "has_more" in data
        assert "interval" in data
        assert len(data["readings"]) <= data["limit"]

    def test_get_meter_history_with_limit(self, client: TestClient) -> None:
        """Test GET /api/v1/meters/{id}/history respects limit parameter."""
        response = client.get("/api/v1/meters/janitza-umg96rm-001/history?limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert len(data["readings"]) <= 10

    def test_get_meter_history_with_interval(self, client: TestClient) -> None:
        """Test GET /api/v1/meters/{id}/history respects interval parameter."""
        response = client.get("/api/v1/meters/janitza-umg96rm-001/history?interval=1hour&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert data["interval"] == "1hour"

    def test_get_meter_history_with_time_range(self, client: TestClient) -> None:
        """Test GET /api/v1/meters/{id}/history with time range."""
        response = client.get(
            "/api/v1/meters/janitza-umg96rm-001/history"
            "?start_time=2024-01-01T00:00:00Z&end_time=2024-01-01T01:00:00Z"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["start_time"] == "2024-01-01T00:00:00Z"
        assert data["end_time"] == "2024-01-01T01:00:00Z"

    def test_get_meter_history_not_found(self, client: TestClient) -> None:
        """Test GET /api/v1/meters/{id}/history returns 404 for unknown meter."""
        response = client.get("/api/v1/meters/unknown-meter/history")

        assert response.status_code == 404


class TestPriceEndpoints:
    """Tests for price endpoints."""

    def test_get_current_price(self, client: TestClient) -> None:
        """Test GET /api/v1/prices/current returns current price."""
        response = client.get("/api/v1/prices/current")

        assert response.status_code == 200
        data = response.json()
        assert "feed_id" in data
        assert "current" in data

        current = data["current"]
        assert "timestamp" in current
        assert "price_eur_per_kwh" in current
        assert "tariff_type" in current
        assert current["price_eur_per_kwh"] >= 0.05  # Price floor

    def test_get_price_forecast(self, client: TestClient) -> None:
        """Test GET /api/v1/prices/forecast returns price forecast."""
        response = client.get("/api/v1/prices/forecast")

        assert response.status_code == 200
        data = response.json()
        assert "feed_id" in data
        assert "forecast" in data
        assert "count" in data
        assert "start_time" in data
        assert "end_time" in data
        assert "interval" in data
        assert len(data["forecast"]) == data["count"]

    def test_get_price_forecast_with_hours(self, client: TestClient) -> None:
        """Test GET /api/v1/prices/forecast respects hours parameter."""
        response = client.get("/api/v1/prices/forecast?hours=6&interval=1hour")

        assert response.status_code == 200
        data = response.json()
        # 6 hours at 1-hour interval = 7 points (including start)
        assert data["count"] >= 6

    def test_get_price_history(self, client: TestClient) -> None:
        """Test GET /api/v1/prices/history returns historical prices."""
        response = client.get("/api/v1/prices/history")

        assert response.status_code == 200
        data = response.json()
        assert "feed_id" in data
        assert "prices" in data
        assert "count" in data
        assert "limit" in data
        assert "has_more" in data

    def test_get_price_history_with_limit(self, client: TestClient) -> None:
        """Test GET /api/v1/prices/history respects limit parameter."""
        response = client.get("/api/v1/prices/history?limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert len(data["prices"]) <= 10

    def test_price_tariff_types_valid(self, client: TestClient) -> None:
        """Test that tariff_type values are valid."""
        response = client.get("/api/v1/prices/forecast?hours=24&interval=1hour")

        assert response.status_code == 200
        data = response.json()

        valid_tariffs = {"night", "morning_peak", "midday", "evening_peak", "evening"}
        for price in data["forecast"]:
            assert price["tariff_type"] in valid_tariffs


class TestSimulationEndpoints:
    """Tests for simulation control endpoints."""

    def test_get_simulation_status(self, client: TestClient) -> None:
        """Test GET /api/v1/simulation/status returns status."""
        response = client.get("/api/v1/simulation/status")

        assert response.status_code == 200
        data = response.json()
        assert "state" in data
        assert "simulation_time" in data
        assert "seed" in data
        assert "acceleration" in data
        assert "registered_entities" in data

    def test_start_simulation(self, client: TestClient) -> None:
        """Test POST /api/v1/simulation/start starts simulation."""
        response = client.post("/api/v1/simulation/start")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        assert "message" in data
        assert "simulation_time" in data

    def test_pause_simulation(self, client: TestClient) -> None:
        """Test POST /api/v1/simulation/pause pauses simulation."""
        # First start
        client.post("/api/v1/simulation/start")

        # Then pause
        response = client.post("/api/v1/simulation/pause")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paused"
        assert "simulation_time" in data

    def test_reset_simulation(self, client: TestClient) -> None:
        """Test POST /api/v1/simulation/reset resets simulation."""
        response = client.post("/api/v1/simulation/reset")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reset"
        assert "seed" in data
        assert "simulation_time" in data

    def test_reset_simulation_with_new_seed(self, client: TestClient) -> None:
        """Test POST /api/v1/simulation/reset with new seed."""
        response = client.post("/api/v1/simulation/reset", json={"seed": 54321})

        assert response.status_code == 200
        data = response.json()
        assert data["seed"] == 54321

    def test_start_with_time(self, client: TestClient) -> None:
        """Test POST /api/v1/simulation/start with start_time."""
        # First reset to ensure clean state
        client.post("/api/v1/simulation/reset")

        response = client.post(
            "/api/v1/simulation/start",
            json={"start_time": "2024-06-15T12:00:00+00:00"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        # Verify the time was set (may have advanced slightly)
        assert "simulation_time" in data


class TestOpenAPIDocs:
    """Tests for OpenAPI documentation."""

    def test_openapi_json_available(self, client: TestClient) -> None:
        """Test that OpenAPI JSON is available."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_docs_available(self, client: TestClient) -> None:
        """Test that Swagger docs are available."""
        response = client.get("/docs")

        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()

    def test_redoc_available(self, client: TestClient) -> None:
        """Test that ReDoc is available."""
        response = client.get("/redoc")

        assert response.status_code == 200


class TestLoadEndpoints:
    """Tests for consumer load endpoints."""

    def test_list_loads(self, client: TestClient) -> None:
        """Test GET /api/v1/loads returns list of consumer loads."""
        response = client.get("/api/v1/loads")

        assert response.status_code == 200
        data = response.json()
        assert "devices" in data
        assert "count" in data
        assert data["count"] >= 1
        assert len(data["devices"]) == data["count"]

    def test_get_load_current(self, client: TestClient) -> None:
        """Test GET /api/v1/loads/{id}/current returns current reading."""
        response = client.get("/api/v1/loads/industrial-oven-001/current")

        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == "industrial-oven-001"
        assert "current" in data

        current = data["current"]
        assert "timestamp" in current
        assert "device_type" in current
        assert "device_state" in current
        assert "device_power_kw" in current

        # Check valid state values
        assert current["device_state"] in ["ON", "OFF"]

        # Power should be non-negative
        assert current["device_power_kw"] >= 0

    def test_get_load_current_not_found(self, client: TestClient) -> None:
        """Test GET /api/v1/loads/{id}/current returns 404 for unknown device."""
        response = client.get("/api/v1/loads/unknown-device/current")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_get_load_history(self, client: TestClient) -> None:
        """Test GET /api/v1/loads/{id}/history returns historical readings."""
        response = client.get("/api/v1/loads/industrial-oven-001/history")

        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == "industrial-oven-001"
        assert "readings" in data
        assert "count" in data
        assert "limit" in data
        assert "has_more" in data
        assert "interval" in data
        assert len(data["readings"]) <= data["limit"]

    def test_get_load_history_with_limit(self, client: TestClient) -> None:
        """Test GET /api/v1/loads/{id}/history respects limit parameter."""
        response = client.get("/api/v1/loads/industrial-oven-001/history?limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert len(data["readings"]) <= 10

    def test_get_load_history_with_interval(self, client: TestClient) -> None:
        """Test GET /api/v1/loads/{id}/history respects interval parameter."""
        response = client.get("/api/v1/loads/industrial-oven-001/history?interval=1hour&limit=5")

        assert response.status_code == 200
        data = response.json()
        assert data["interval"] == "1hour"

    def test_get_load_history_with_time_range(self, client: TestClient) -> None:
        """Test GET /api/v1/loads/{id}/history with time range."""
        response = client.get(
            "/api/v1/loads/industrial-oven-001/history"
            "?start_time=2024-01-01T08:00:00Z&end_time=2024-01-01T09:00:00Z"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["start_time"] == "2024-01-01T08:00:00Z"
        assert data["end_time"] == "2024-01-01T09:00:00Z"

    def test_get_load_history_not_found(self, client: TestClient) -> None:
        """Test GET /api/v1/loads/{id}/history returns 404 for unknown device."""
        response = client.get("/api/v1/loads/unknown-device/history")

        assert response.status_code == 404

    def test_load_operating_window_weekday(self, client: TestClient) -> None:
        """Test that load operates during weekday operating windows."""
        # 2024-01-02 is a Tuesday, 08:00 should be in operating window (07-09)
        response = client.get(
            "/api/v1/loads/industrial-oven-001/history"
            "?start_time=2024-01-02T08:00:00Z&end_time=2024-01-02T08:30:00Z&limit=3"
        )

        assert response.status_code == 200
        data = response.json()
        assert "readings" in data
        # Readings should exist for operating window
        assert len(data["readings"]) > 0

    def test_load_no_operation_weekend(self, client: TestClient) -> None:
        """Test that load does not operate on weekends."""
        # 2024-01-06 is a Saturday
        response = client.get(
            "/api/v1/loads/industrial-oven-001/history"
            "?start_time=2024-01-06T08:00:00Z&end_time=2024-01-06T09:00:00Z&limit=5"
        )

        assert response.status_code == 200
        data = response.json()
        # All readings on weekend should be OFF
        for reading in data["readings"]:
            assert reading["device_state"] == "OFF"
            assert reading["device_power_kw"] == 0.0

    def test_load_no_operation_outside_window(self, client: TestClient) -> None:
        """Test that load does not operate outside operating windows."""
        # 2024-01-02 is a Tuesday, 22:00 is outside all windows (07-09, 11-13, 15-17)
        response = client.get(
            "/api/v1/loads/industrial-oven-001/history"
            "?start_time=2024-01-02T22:00:00Z&end_time=2024-01-02T23:00:00Z&limit=5"
        )

        assert response.status_code == 200
        data = response.json()
        # All readings outside window should be OFF
        for reading in data["readings"]:
            assert reading["device_state"] == "OFF"
            assert reading["device_power_kw"] == 0.0

    def test_load_power_when_on(self, client: TestClient) -> None:
        """Test that load has rated power when ON."""
        # Get readings during operating window
        response = client.get(
            "/api/v1/loads/industrial-oven-001/history"
            "?start_time=2024-01-02T08:00:00Z&end_time=2024-01-02T08:45:00Z&limit=10"
        )

        assert response.status_code == 200
        data = response.json()

        # Check ON readings have power close to rated (with ±10% variation), OFF readings have 0
        rated_power = 3.0
        for reading in data["readings"]:
            if reading["device_state"] == "ON":
                # Allow ±10% variation from rated power
                assert 0.9 * rated_power <= reading["device_power_kw"] <= 1.1 * rated_power
            else:
                assert reading["device_power_kw"] == 0.0


class TestDataConsistency:
    """Tests for data consistency and determinism."""

    def test_same_timestamp_same_data(self, client: TestClient) -> None:
        """Test that same timestamp produces same data."""
        # Get history for a specific time range
        url = (
            "/api/v1/meters/janitza-umg96rm-001/history"
            "?start_time=2024-01-01T12:00:00Z&end_time=2024-01-01T12:15:00Z&limit=1"
        )

        response1 = client.get(url)
        response2 = client.get(url)

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()

        # Readings should be identical
        assert data1["readings"] == data2["readings"]

    def test_price_determinism(self, client: TestClient) -> None:
        """Test that prices are deterministic."""
        url = (
            "/api/v1/prices/history"
            "?start_time=2024-01-01T12:00:00Z&end_time=2024-01-01T12:15:00Z&limit=1"
        )

        response1 = client.get(url)
        response2 = client.get(url)

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()

        # Prices should be identical
        assert data1["prices"] == data2["prices"]

    def test_load_determinism(self, client: TestClient) -> None:
        """Test that consumer load readings are deterministic."""
        url = (
            "/api/v1/loads/industrial-oven-001/history"
            "?start_time=2024-01-02T08:00:00Z&end_time=2024-01-02T08:15:00Z&limit=1"
        )

        response1 = client.get(url)
        response2 = client.get(url)

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = response1.json()
        data2 = response2.json()

        # Load readings should be identical
        assert data1["readings"] == data2["readings"]
