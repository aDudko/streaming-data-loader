# Streaming Data Loader

## Overview

Streaming Data Loader is a tool for efficiently loading and processing streaming data from Kafka into Elasticsearch. The
project implements asynchronous message processing, provides fault tolerance, and uses batch insertion of data into the
repository. With the addition of observability, the project now includes detailed monitoring and metrics collection to
ensure high availability and performance.

### Key features of the  project:

This project is an asynchronous data loader from Kafka to Elasticsearch, providing stable processing of data streams
with high performance and comprehensive monitoring.

### Main features:

- **Asynchronous**: Using `asyncio`, `aiokafka` and `aiohttp` minimizes data processing latency.
- **Configuration flexibility**: Uses `pydantic-settings`, allowing easy customization of settings via `.env`.
- **Reliable data processing**: Supports batch loading, retries on failures, and error logging.
- **Scalability**: Support for Kafka `consumer groups` for distributed data processing.
- **Docker integration**: Can be deployed via `docker-compose`.
- **Observability**: Integrated with `Prometheus` and `Grafana` for real-time monitoring and alerting.

### Differences from analogs:

- **Minimal processing latency**
    - Most similar solutions process data in streaming mode, but do not always use asyncio.
    - Here, all operations are asynchronous, which reduces blocking and increases throughput.

- **Flexible and easy to customize**
    - Unlike heavyweight ETL solutions (Logstash, Flume), this project does not require complex customization and is
      easy to adapt.

- **Automatic repetition of operations in case of failures**
    - Kafka and Elasticsearch often experience temporary failures.
    - This service includes multiple connection attempts and reinsertion mechanisms when failures occur.

- **Logging and debugging**
    - A logging system (`python-json-logger`) is built in, making it easy to monitor and analyze performance.

- **Comprehensive monitoring**
    - Integrated with Prometheus for metrics collection and Grafana for visualization.
    - Provides detailed insights into system performance and health.

## Technologies

- `Python` v3.12
- `Kafka` message broker
- `Elasticsearch` data warehouse
- `aiokafka` asynchronous Kafka client
- `aiohttp` asynchronous HTTP client
- `pydantic` data validation
- `poetry` dependency management
- `Prometheus` metrics collection 
- `Grafana` metrics visualization

## Architecture

This project is built on a port-to-adapter architecture (`Hexagonal Architecture`), providing flexibility and scalability.

### Overview of the architecture

- **Input Ports** - Kafka
    - Messages from Kafka are read by the asynchronous Kafka Consumer (`aiokafka`).
    - Batch processing is used to improve performance.
    - Supports deserialization of data before processing.

- **Business Logic** - Application Core
    - Apply data models (Pydantic) for validation and event transformation.
    - All data processing takes place in an asynchronous event processing service (event_service).
    - Flexibility of customization is provided through pydantic-settings.

- **Output Ports** - Elasticsearch
    - Asynchronous Elasticsearch client (`elasticsearch-py`) is used.
    - Records are inserted into the index in batches (`Bulk API`), which increases loading speed.
    - Built-in retry on connection failures.

- **Infrastructure Layer** - Docker and Logging
    - Docker-compose manages the startup of all services (Kafka, Elasticsearch, Streaming Data Loader).
    - Logging (`python-json-logger`) for detailed analysis of service performance.
    - Monitoring (`Prometheus` and `Grafana`) for real-time metrics visualization and alerting.

## Structure of the project

```
streaming-data-loader/
├── src/                            # project sources
│   ├── domain/                     # models definition
│   ├── ports/
│   │   ├── input                   # application input ports
│   │   └── output                  # application output ports
│   ├── services/                   # processing logic
│   ├── config.py
│   ├── logger.py
│   ├── metrics.py                  # metrics collection and monitoring
│   └── utility.py
├── tests/
├── compose.yml                     # docker-compose file
├── Dockerfile
├── main.py
└── pyproject.toml                  # requirements
```

### Main components

- **KafkaConsumerService** - responsible for reading messages from Kafka, deserializing them, and passing them to the
  event service.
- **ElasticsearchClientService** - provides connection to Elasticsearch, as well as batch insertion of data with error
  handling.
- **EventModel** - converts input events before loading them into Elasticsearch.
- **MetricsService** - collects and exposes metrics for monitoring system performance and health.

## Monitoring and Observability

The project now includes comprehensive monitoring and observability features:

- **Prometheus**: Collects metrics from the application, including message processing rates, error counts, and processing times.
- **Grafana**: Provides dashboards for visualizing metrics and setting up alerts.
- **Metrics**: Key metrics include:
  - `messages_processed_total`: Total number of processed messages. 
  - `errors_total`: Total number of errors encountered. 
  - `consume_duration_seconds`: Time spent consuming messages. 
  - `response_duration_seconds`: Time spent to response. 
  - `transform_duration_seconds`: Time spent transforming messages.
  - `batch_processing_duration_seconds`: Time spent processing the entire batch.

## Author:

Anatoly Dudko
