# Streaming Data Loader

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org)
[![Kafka](https://img.shields.io/badge/Kafka-Streaming-red)](https://kafka.apache.org/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-Search-yellow)](https://www.elastic.co/elasticsearch/)
[![Prometheus](https://img.shields.io/badge/Monitoring-Prometheus-orange)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Dashboards-Grafana-brightgreen)](https://grafana.com/)
[![AsyncIO](https://img.shields.io/badge/Async-Enabled-lightgrey)](https://docs.python.org/3/library/asyncio.html)
[![CI](https://img.shields.io/badge/Tests-Pytest-green)](https://docs.pytest.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/K8s-Supported-blueviolet)](https://kubernetes.io/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

---

## Overview

**Streaming Data Loader** is a high-performance, async-powered microservice for processing data streams from **Kafka**
and bulk-loading them into **Elasticsearch**. It combines modern Python tooling with observability best practices to
provide **reliable, scalable, and debuggable data pipelines**.

It’s fast, resilient, and production-ready — ideal for those who need lightweight alternatives to complex ETL systems.

---

## Key Features

- **Asynchronous processing** with `asyncio`, `aiokafka`, and `aiohttp`
- **Batch insertions** for throughput efficiency
- **Retry & fault-tolerant** logic for Kafka and Elasticsearch
- **Configurable** via `.env` and `pydantic-settings`
- **Docker & Kubernetes ready**
- **Prometheus + Grafana** monitoring included
- **Tested** with `pytest`, including integration scenarios

---

## Quick Start

### 🐳 Docker Compose

```bash
docker-compose up --build
```

- http://localhost:9090 → Prometheus
- http://localhost:3000 → Grafana (admin / admin)
- http://localhost:8080 → Kafka UI

### ☸️ Kubernetes

#### Step 1 — Deploy

```bash
./deploy.sh
```

#### Step 2 — Cleanup

```bash
./clean.sh
```

---

## Architecture

This project uses **Hexagonal Architecture** (Ports and Adapters), ensuring modularity, extensibility, and clean separation of concerns.

```text
Kafka -→ KafkaConsumerService -→ EventService -→ ElasticsearchClientService -→ Elasticsearch
                         │                ↓
                         └-→ Metrics + Logging (Prometheus + JSON logs)
```

### Layers

- **Input Ports**: Kafka Consumer (aiokafka), deserialization, batching
- **Application Core**: Event transformation, validation, retry logic
- **Output Ports**: Async Elasticsearch client, bulk insert, failure handling
- **Infrastructure**: Docker, Kubernetes, logging, metrics, monitoring

---

## 🔍 Why Choose This Over Logstash, Flume, etc.?

- ✅ **True async** data pipeline — lower latency, better throughput
- ✅ **No heavyweight config DSL** — Python code, `pyproject.toml`, `.env`
- ✅ **Built-in retries & fault handling** — robust out of the box
- ✅ **JSON logging** and metric labeling for full observability
- ✅ **Open-source & customizable** — perfect for modern data teams

---

## Observability

Prometheus scrapes metrics on `/metrics` (port `8000`). Dashboards are automatically provisioned in Grafana.

| Metric                              | Description                        |
|-------------------------------------|------------------------------------|
| `messages_processed_total`          | Total number of processed messages |
| `errors_total`                      | Total errors during processing     |
| `consume_duration_seconds`          | Time spent reading from Kafka      |
| `response_duration_seconds`         | Time to insert into Elasticsearch  |
| `transform_duration_seconds`        | Time spent transforming messages   |
| `batch_processing_duration_seconds` | Full batch processing time         |

---

## Testing

```bash
pytest -v
```

Includes:

- ✅ Unit tests
- ✅ Integration tests (Kafka → ES)
- ✅ Metrics verification
- ✅ Config validation

---

## Technologies

- `Python 3.12` + `asyncio`
- `Kafka + aiokafka`
- `Elasticsearch` `Bulk API`
- `Pydantic` `dotenv` `poetry`
- `Prometheus` `Grafana`
- `Docker` `docker-compose`
- `Kubernetes-ready`
- JSON logging (`python-json-logger`)

---

## Project Structure

```text
streaming-data-loader/
├── configs/                     # Prometheus / Grafana
├── src/                         # Main source code
│   ├── domain/
│   ├── ports/
│   ├── services/                # Event processing logic
│   ├── config.py                # Settings & env config
│   ├── logger.py                # JSON logger setup
│   └── metrics.py               # Prometheus metrics
├── tests/                       # Unit & integration tests
├── k8s/                         # Kubernetes manifests
├── docker-compose.yml
├── Dockerfile
├── deploy.sh / clean.sh
└── pyproject.toml
```

---

## If you find this useful...

...give it a star, fork it, or mention it in your next data project!

## Author

**Anatoly Dudko**  
[GitHub @aDudko](https://github.com/aDudko) • [LinkedIn](https://www.linkedin.com/in/dudko-anatol/)
