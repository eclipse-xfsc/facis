# Digital Contracting Service
Preliminary design, experiments, and preparatory work for the Digital Contracting Service (DCS) API server, conducted prior to the creation of the official Eclipse project repositories. This repository is not an official Eclipse Foundation project and does not host canonical project source code.

## Repository Structure

```
.
├── cmd/
│   ├── dcs/          # HTTP API server entrypoint
│   └── dcs-cli/      # (optional) CLI tooling
├── design/           # Goa DSL (API contracts)
│   └── design.go
├── gen/              # Goa-generated transport & types (DO NOT EDIT)
├── internal
|   └── datatype/     # Used data types for the application
|   └── controller/  # Application endpoints implementations
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
