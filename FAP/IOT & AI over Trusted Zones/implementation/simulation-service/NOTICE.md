# Notices for FACIS FAP IoT & AI Simulation Service

This content is produced and maintained by the ATLAS IoT Lab GmbH
in the context of the Eclipse FACIS project.

## Project Information

- **Project:** Eclipse FACIS — Federation Architecture Pattern: IoT & AI Demonstrator
- **Project Home:** https://projects.eclipse.org/projects/technology.facis
- **License:** Apache License 2.0

## Copyright

Copyright (c) 2025–2026 ATLAS IoT Lab GmbH.

## Third-Party Content

This project includes or depends on the following third-party software:

| Package | License | Usage |
|---|---|---|
| FastAPI | MIT | HTTP REST API framework |
| uvicorn | BSD-3-Clause | ASGI server |
| paho-mqtt | EPL-2.0 | MQTT client |
| pymodbus | BSD-3-Clause | Modbus TCP server |
| numpy | BSD-3-Clause | Numerical computation |
| pydantic | MIT | Data validation |
| confluent-kafka | Apache-2.0 | Kafka producer |
| httpx | BSD-3-Clause | Async HTTP client |
| PyYAML | MIT | YAML configuration |
| pytest | MIT | Testing framework |
| pytest-bdd | MIT | BDD testing |
| Eclipse Mosquitto | EPL-2.0 | MQTT broker (Docker) |
| Apache Kafka | Apache-2.0 | Message broker (runtime) |
| Apache NiFi | Apache-2.0 | Data ingestion (runtime) |
| Trino | Apache-2.0 | Query engine (runtime) |
| Apache Iceberg | Apache-2.0 | Table format (runtime) |
| Node-RED | Apache-2.0 | ORCE orchestration (runtime) |
| node-red-contrib-rdkafka | MIT | Kafka producer for Node-RED |

## Cryptography

This project does not include cryptographic software directly. TLS/mTLS certificates
for Kafka and Trino communication are provisioned by the Stackable platform operator
and are not bundled with this distribution.
