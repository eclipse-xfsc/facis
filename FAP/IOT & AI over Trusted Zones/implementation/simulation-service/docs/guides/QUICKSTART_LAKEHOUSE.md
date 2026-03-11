# Lakehouse Quick Start — Reproduction Guide

**Project:** FACIS FAP – IoT & AI Demonstrator
**Scope:** Bronze → Silver → Gold Medallion architecture on Trino + Iceberg

This guide walks through setting up, validating, and querying the FACIS Lakehouse from scratch. For full technical details, see [lakehouse-reference.md](lakehouse-reference.md).

---

## Prerequisites

| Requirement | Detail |
|---|---|
| Python | 3.11+ |
| Network access | Reachable: `212.132.83.150:8443` (Trino), `identity.facis.cloud` (Keycloak) |
| Keycloak credentials | Username, password, and OIDC client secret for the `facis` realm |
| Git checkout | Branch `FC-167` (or later) with WP3 completion |

## Step 1: Install Dependencies

```bash
cd "FAP/IOT & AI over Trusted Zones/implementation/simulation-service"

# Install the simulation-service package with lakehouse extras
pip install -e ".[lakehouse]"
```

This installs: `trino>=0.328.0`, `requests>=2.31.0`, `python-dotenv>=1.0.0`, `tabulate>=0.9.0`.

## Step 2: Configure Credentials

```bash
# Copy the example file
cp .env.cluster.example .env.cluster

# Edit with your credentials
# Required values:
#   FACIS_OIDC_USERNAME   — Keycloak user (e.g. 'test')
#   FACIS_OIDC_PASSWORD   — Keycloak password
#   FACIS_OIDC_CLIENT_SECRET — OIDC client secret (Keycloak → Clients → OIDC → Credentials)
```

The service endpoint defaults (`FACIS_KEYCLOAK_URL`, `FACIS_TRINO_HOST`, etc.) are pre-filled for the demo cluster. Override only if connecting to a different environment.

## Step 3: Create the Lakehouse

```bash
python scripts/setup_lakehouse.py --env-file .env.cluster
```

This creates:

- **3 schemas:** `bronze`, `silver`, `gold` in the Trino catalog
- **9 Bronze Iceberg tables** (Parquet on S3, partitioned by day)
- **9 Silver views** with data quality filtering, derived fields, and schema evolution
- **12 Gold views** with aggregated KPIs and anomaly detection

Expected output: 24 `CREATE` statements executed without errors.

## Step 4: Verify Data Flow

Bronze tables are populated by the NiFi pipeline consuming from Kafka. To check if data is flowing:

```bash
python scripts/validate_lakehouse.py --env-file .env.cluster
```

Expected output: **39/39 checks PASSED**

The 39 checks cover:

| Category | Checks | What it verifies |
|---|---|---|
| Bronze | 9 | All Iceberg tables contain data |
| Silver (data) | 9 | All views return typed records |
| Silver (derived) | 5 | Computed fields exist and are valid |
| Gold | 12 | All aggregation views return data |
| Cross-layer | 3 | Ratios and indices within expected ranges |

If Bronze tables are empty, data ingestion hasn't started yet — see the [NiFi setup guide](../deployment/ops-runbook.md).

## Step 5: Query the Gold Layer

Connect to Trino (via CLI, DBeaver, or Superset) and explore:

```sql
-- Smart Energy: daily cost breakdown
SELECT * FROM gold.energy_cost_daily LIMIT 10;

-- Smart Energy: PV self-consumption analysis
SELECT * FROM gold.pv_self_consumption_daily LIMIT 10;

-- Smart City: combined zone KPIs
SELECT * FROM gold.city_dashboard_summary LIMIT 10;

-- AI input: statistical outliers (may be empty for well-behaved data)
SELECT * FROM gold.anomaly_candidates LIMIT 10;
```

Full Gold view inventory (12 views):

| View | Domain | Granularity |
|---|---|---|
| `energy_balance_hourly` | Smart Energy | Hourly × meter |
| `pv_performance_hourly` | Smart Energy | Hourly × PV system |
| `net_grid_hourly` | Smart Energy | Hourly (cross-feed) |
| `weather_hourly` | Smart Energy | Hourly |
| `energy_cost_daily` | Smart Energy | Daily × meter |
| `pv_self_consumption_daily` | Smart Energy | Daily |
| `device_utilization_daily` | Smart Energy | Daily × device |
| `streetlight_zone_hourly` | Smart City | Hourly × zone |
| `event_impact_daily` | Smart City | Daily × zone × type |
| `traffic_pattern_hourly` | Smart City | Hourly × zone |
| `city_dashboard_summary` | Smart City | Daily × zone |
| `anomaly_candidates` | AI Pipeline | Per-event (statistical) |

## Teardown

To remove all views, tables, and schemas:

```bash
python scripts/setup_lakehouse.py --env-file .env.cluster --teardown
```

## Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| `401 Invalid credentials` | OIDC token expired or wrong credentials | Check `.env.cluster` credentials; tokens are short-lived, scripts auto-refresh |
| `SCHEMA_NOT_FOUND` | Schemas not created yet | Run `setup_lakehouse.py` (without `--teardown`) |
| Bronze tables empty | NiFi not ingesting from Kafka | Run `setup_nifi.py --env-file .env.cluster`, verify Kafka topics have data |
| `AUTOCOMMIT_WRITE_CONFLICT` | Concurrent NiFi inserts | Transient; NiFi retries automatically |
| Gold view returns NULL | Time alignment mismatch in cross-feed joins | Expected for `net_grid_hourly` price column; use `energy_cost_daily` for cost data |
| `anomaly_candidates` empty | No statistical outliers in current dataset | Expected behavior — view populates when data exceeds 2σ from mean |
| Connection timeout | Trino overloaded or network issues | Retry; check that `212.132.83.150:8443` is reachable |
| `pip install` fails | Missing Python 3.11+ | Verify `python --version` is 3.11 or later |

---

For full schema definitions, derived field formulas, and architecture details, see [lakehouse-reference.md](lakehouse-reference.md).

© ATLAS IoT Lab GmbH — FACIS FAP IoT & AI Demonstrator
