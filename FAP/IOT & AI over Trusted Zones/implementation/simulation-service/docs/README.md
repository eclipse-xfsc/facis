# FACIS FAP IoT & AI — Documentation

This directory contains the deliverable documentation for the FACIS Federation Architecture Pattern (FAP) IoT & AI Demonstrator, developed by ATLAS IoT Lab GmbH under the Eclipse Foundation's FACIS project.

All documentation follows the [Eclipse Foundation Project Handbook](https://www.eclipse.org/projects/handbook/) guidelines for open-source project deliverables.

## Structure

```
docs/
├── README.md                         (this file)
├── architecture/
│   └── system-architecture.md        System architecture and data flow
├── deployment/
│   ├── deployment-operations.md      Deployment procedures and operations
│   ├── orce-cluster-deployment.md    ORCE manual registry-free cluster deployment
│   ├── infrastructure-prerequisites.md  Platform requirements for the infrastructure team
│   └── ops-runbook.md                Operations runbook (Helm, Docker, troubleshooting)
├── api/
│   ├── rest-api.md                   REST API reference
│   ├── mqtt-reference.md             MQTT topic and payload reference
│   └── modbus-reference.md           Modbus TCP register map
├── data-model/
│   ├── schema-reference.md           Data schema reference (all feeds)
│   ├── avro-schema-reference.md      Avro schemas — Bronze & Silver layers
│   └── data-structures-semantics.md  Data structures, semantics & relationships
├── guides/
│   ├── index.md                      Developer guide — overview and quickstart
│   ├── setup.md                      Development environment setup
│   ├── architecture.md               Component design and data flow
│   ├── configuration.md              All configuration options reference
│   ├── extending.md                  How to add new simulator feed types
│   └── lakehouse-reference.md        Lakehouse layer reference (Bronze/Silver/Gold)
├── pipeline/
│   └── mqtt-kafka-bronze-pipeline.md MQTT → Kafka Bronze ingestion pipeline
└── milestone-reports/
    ├── MS2_Technical_Reference.md    MS2 end-to-end technical reference
    └── MS2_Demo_Guide.md            MS2 demo walkthrough
```

## Conventions

- All timestamps use ISO 8601 format with UTC (`Z` suffix)
- Configuration examples use placeholder values (`<value>`) for any sensitive data
- File paths shown are relative to the `simulation-service/` root unless stated otherwise
- SQL examples reference the Trino catalog `fap-iotai-stackable` with Iceberg connector

## License

This documentation is provided under the Apache License 2.0 — see [LICENSE](../LICENSE) in the project root.

© ATLAS IoT Lab GmbH — Provided in the context of the FACIS project under the Eclipse Foundation.
