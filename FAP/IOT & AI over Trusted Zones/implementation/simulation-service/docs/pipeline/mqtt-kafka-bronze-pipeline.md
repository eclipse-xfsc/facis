# MQTT → Kafka Bronze Pipeline

## Overview

This pipeline consumes MQTT messages published by the FACIS simulation service
and lands them in Kafka Bronze topics with ingestion metadata enrichment. It
forms the first stage of the data lakehouse ingestion — bridging real-time MQTT
telemetry into the Kafka event backbone used by the downstream Kafka→Trino
Bronze ingestion pipeline (`setup_nifi.py`).

```
┌──────────────┐     ┌─────────────┐     ┌───────────────┐     ┌──────────────┐
│  Simulation   │────▶│  Mosquitto   │────▶│  NiFi 2.x     │────▶│  Kafka       │
│  Service      │MQTT │  Broker      │     │  Pipeline      │     │  Bronze      │
│  (Publisher)  │     │  :1883       │     │  (5 routes)    │     │  Topics      │
└──────────────┘     └─────────────┘     └───────┬───────┘     └──────────────┘
                                                  │ failure
                                                  ▼
                                          ┌──────────────┐
                                          │  Dead-Letter  │
                                          │  Queue (DLQ)  │
                                          └──────────────┘
```

## Topic Mapping

| # | MQTT Subscription         | QoS | Kafka Bronze Topic                | Description                                  |
|---|---------------------------|-----|-----------------------------------|----------------------------------------------|
| 1 | `facis/energy/meter/+`    | 1   | `energy.bronze.meter-readings`    | 3-phase energy meter readings                |
| 2 | `facis/prices/spot`       | 1   | `energy.bronze.prices`            | Spot electricity prices                      |
| 3 | `facis/weather/current`   | 0   | `energy.bronze.weather`           | Weather conditions (temperature, irradiance) |
| 4 | `facis/energy/pv/+`       | 1   | `energy.bronze.pv-generation`     | PV generation data (power, efficiency)       |
| 5 | `facis/loads/+`           | 0   | `energy.bronze.consumer-states`   | Consumer device load states                  |
| — | *(failures)*              | —   | `energy.bronze.dead-letter`       | Failed enrichment or Kafka publish           |

MQTT wildcard `+` matches a single level, so `facis/energy/meter/+` subscribes
to all meter IDs (e.g., `facis/energy/meter/meter-001`).

## Processor Chain

Each of the 5 MQTT subscriptions gets an independent 4-processor chain:

```
ConsumeMQTT ──▶ UpdateAttribute ──▶ ReplaceText ──▶ PublishKafka
   (MQTT)         (set dest)        (enrich)        (produce)
                                                        │
                                                   [failure]
                                                        ▼
                                                  PublishKafka (DLQ)
```

### 1. ConsumeMQTT

Subscribes to the MQTT topic pattern on the Mosquitto broker. Each processor
gets a unique `Client ID` to avoid session conflicts. Messages arrive as
FlowFiles with the attribute `mqtt.topic` set to the actual topic string.

### 2. UpdateAttribute

Sets `kafka.destination` to the target Bronze Kafka topic name. This attribute
is used downstream for routing and debugging.

### 3. ReplaceText (Metadata Enrichment)

Wraps the original JSON payload in a Bronze envelope using NiFi Expression
Language. The replacement template:

```
{
  "ingest_timestamp": "${now():format('yyyy-MM-dd''T''HH:mm:ss.SSS''Z''','UTC')}",
  "source_system": "facis-simulation-service",
  "source_topic": "${mqtt.topic}",
  "payload": <original JSON>
}
```

The `(?s)(^.*$)` regex captures the entire FlowFile content (including
newlines), and `$1` inserts it as the `payload` value.

### 4. PublishKafka

Produces to the target Bronze topic with:

- **Delivery Guarantee**: `DELIVERY_REPLICATED` (acks=all)
- **Compression**: LZ4
- **Message Key**: `${mqtt.topic}` for deterministic partitioning
- **Headers**: All `mqtt.*` attributes forwarded as Kafka headers

### 5. Dead-Letter Queue (DLQ)

All PublishKafka failure relationships route to a shared DLQ publisher that
writes to `energy.bronze.dead-letter`. The DLQ preserves all FlowFile
attributes (including original MQTT topic, timestamps) for debugging.

## Bronze Envelope Schema

Every message arriving in a Kafka Bronze topic has this structure:

```json
{
  "ingest_timestamp": "2026-03-07T14:30:00.123Z",
  "source_system": "facis-simulation-service",
  "source_topic": "facis/energy/meter/meter-001",
  "payload": {
    "timestamp": "2026-03-07T14:30:00.000Z",
    "meter_id": "meter-001",
    "site_id": "site-berlin-001",
    "readings": {
      "active_power_kw": 45.23,
      "voltage": { "L1": 230.5, "L2": 231.2, "L3": 229.8 }
    }
  }
}
```

| Field             | Type   | Source                          | Description                           |
|-------------------|--------|---------------------------------|---------------------------------------|
| `ingest_timestamp`| string | NiFi `${now()}` expression      | ISO-8601 UTC timestamp at ingestion   |
| `source_system`   | string | Constant                        | Always `facis-simulation-service`     |
| `source_topic`    | string | FlowFile `mqtt.topic` attribute | Original MQTT topic the message was on|
| `payload`         | object | Original FlowFile content       | Unmodified MQTT JSON payload          |

## Deployment

### Local (Docker Compose)

The local stack uses plaintext connections to the Mosquitto and Kafka containers
defined in `docker-compose.yml`:

```bash
# Start infrastructure
docker compose up -d mqtt kafka

# Deploy NiFi pipeline (requires NiFi running)
python scripts/setup_nifi_mqtt_to_kafka.py --env-file .env.cluster

# Dry run (preview only)
python scripts/setup_nifi_mqtt_to_kafka.py --env-file .env.cluster --dry-run

# Teardown
python scripts/setup_nifi_mqtt_to_kafka.py --env-file .env.cluster --teardown
```

Environment:

| Service | Host      | Port |
|---------|-----------|------|
| MQTT    | `mqtt`    | 1883 |
| Kafka   | `kafka`   | 9092 |

### Cluster (Stackable K8s)

In the production cluster, all connections use Stackable TLS (PKCS12 keystores
mounted at `/stackable/server_tls/`):

```bash
python scripts/setup_nifi_mqtt_to_kafka.py \
    --env-file .env.cluster \
    --cluster
```

Environment:

| Service | Host                                                        | Port |
|---------|-------------------------------------------------------------|------|
| MQTT    | `facis-mqtt.stackable.svc.cluster.local`                    | 1883 |
| Kafka   | `kafka-broker-default-bootstrap.stackable.svc.cluster.local`| 9093 |

## Error Handling

### Dead-Letter Queue

Messages that fail enrichment (malformed JSON) or Kafka publishing (broker
unavailable, topic not writable) are routed to `energy.bronze.dead-letter`. The
DLQ message preserves all FlowFile attributes for root-cause analysis:

- `mqtt.topic` — original MQTT topic
- `kafka.destination` — intended Kafka topic
- `error.message` — NiFi error description

### Back-Pressure

Connections between processors have back-pressure thresholds:

- **Object threshold**: 10,000 FlowFiles
- **Data size threshold**: 1 GB

When thresholds are reached, upstream processors pause until the queue drains.

### Monitoring Alerts

| Condition                               | Severity | Action                            |
|-----------------------------------------|----------|-----------------------------------|
| Queue depth > 5,000 on any connection   | WARN     | Check Kafka broker health         |
| DLQ receives > 0 messages in 5 minutes  | ERROR    | Investigate failed messages       |
| ConsumeMQTT shows DISCONNECTED          | CRITICAL | Check Mosquitto broker status     |

## Testing

### Unit Tests (no infrastructure)

```bash
pytest tests/integration/test_mqtt_kafka_pipeline.py -v -k "TestMetadataEnrichment or TestTopicMapping or TestPipelineSetupScript"
```

### Integration Tests (requires Docker Compose + NiFi)

```bash
# Start infrastructure
docker compose up -d mqtt kafka

# Deploy NiFi pipeline
python scripts/setup_nifi_mqtt_to_kafka.py --env-file .env.cluster

# Run integration tests
pytest tests/integration/test_mqtt_kafka_pipeline.py -v -k "TestEndToEndPipeline"
```

### What the tests verify

- **TestMetadataEnrichment**: Bronze envelope structure, ISO-8601 timestamps, payload preservation
- **TestTopicMapping**: All 5 routes defined, naming convention, correct source→destination pairs
- **TestMQTTPublish**: MQTT publish succeeds for each feed topic
- **TestEndToEndPipeline**: Messages arrive in correct Kafka topics, metadata enriched, payload unmodified, no data loss (20-message batch)
- **TestKafkaTopics**: Bronze topics exist in Kafka
- **TestPipelineSetupScript**: Setup script exists, is valid Python, flow JSON is valid

## Files

| File | Purpose |
|------|---------|
| `scripts/setup_nifi_mqtt_to_kafka.py` | NiFi REST API script to deploy the pipeline |
| `nifi/templates/mqtt-to-kafka-bronze-flow.json` | Portable flow definition (JSON) |
| `tests/integration/test_mqtt_kafka_pipeline.py` | Unit + integration tests |
| `docs/pipeline/mqtt-kafka-bronze-pipeline.md` | This documentation |

## Relationship to Existing Pipelines

This pipeline sits between the simulation service and the existing Kafka→Trino
ingestion pipeline:

```
Simulation ──MQTT──▶ [THIS PIPELINE] ──Kafka──▶ setup_nifi.py ──Trino──▶ Bronze Tables
```

The existing `setup_nifi.py` consumes from `sim.smart_energy.*` topics. The new
Bronze topics (`energy.bronze.*`) use a different naming convention to
distinguish MQTT-sourced messages from direct Kafka publishes. Both feed into
the same Bronze Iceberg tables via the Trino ingestion layer.
