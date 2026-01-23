# Digital Contracting Service
Preliminary design, experiments, and preparatory work for the Digital Contracting Service (DCS) API server, conducted prior to the creation of the official Eclipse project repositories. This repository is not an official Eclipse Foundation project and does not host canonical project source code.

## Repository Structure

```
.
├── cmd/
│   ├── dcs/          # HTTP API server entrypoint
│   └── dcs-cli/      # (optional) CLI tooling
├── design/           # Goa DSL (API contracts)
│   └── contract_storage_archive.go # Design description for the Contract Storage Archive api
│   └── contract_workflow_eninge.go # Design description for the Contract Workflow Engine api
│   └── dcs_to_dcs.go               # Design description for the DCS to DCS communication api
│   └── design.go                   # Goa main design description
│   └── external_system_api.go      # Design description for the external system communication api
│   └── orchestration_webhook.go    # Design description for the orchestration webhooks api
│   └── pac.go                      # Design description for the Process Audit & Compliance Management api
│   └── signature_management.go     # Design description for the Signature Management api
│   └── template_catalogue_integration.go   # Design description for the Template Catalogue integration api
│   └── template_repository.go      # Design description for the Template Repository api
├── gen/              # Goa-generated transport & types (DO NOT EDIT)
├── internal
|   └── datatype/     # Used data types for the application
│   └── service/      # Application service implementations
├── go.mod
├── go.sum
└── README.md
```

## Prerequisites

- Go **1.25+**
- Goa **v3**

## Setup & Build

Initialize dependencies:

```
go mod tidy
```

Generate the Goa code under `gen/` after modifying `design/design.go`:

```
goa gen design
```


## Running the API Server

```
go run ./cmd/dcs
```

## Example Request

```
curl http://0.0.0.0:8991/template/search
```
