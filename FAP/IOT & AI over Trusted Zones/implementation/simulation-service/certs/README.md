# TLS Certificates for Kafka

This directory should contain the TLS certificates for connecting to the
remote Kafka cluster at `212.132.83.222:9093`.

## Required Files

| File | Description |
|------|-------------|
| `ca.crt` | CA certificate (cluster root CA) |
| `client.crt` | Client certificate (signed by the cluster CA) |
| `client.key` | Client private key |

## How to Obtain

1. Request certificates from the cluster administrator
2. Place all three files in this directory
3. Ensure `client.key` has restricted permissions: `chmod 600 client.key`

## Usage

Set `FACIS_ENV=cluster` to activate the cluster configuration, which
references these certificate paths automatically.

These files are `.gitignore`d and must not be committed to the repository.
