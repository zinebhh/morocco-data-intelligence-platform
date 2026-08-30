# System Architecture

## 1. Overview

The Morocco Data Intelligence Platform follows a modular, layered and cloud-ready architecture.

The architecture separates data collection, storage, processing, analytics, artificial intelligence and application services.

The main architecture is:

```text
                           ┌─────────────────────┐
                           │    DATA SOURCES     │
                           │                     │
                           │ APIs / Web / PDFs   │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │      INGESTION      │
                           │                     │
                           │ Python Collectors   │
                           │ Scrapers / APIs     │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │      AIRFLOW        │
                           │   Orchestration     │
                           └──────────┬──────────┘
                                      │
                                      ▼
                     ┌────────────────────────────────┐
                     │          DATA LAKE              │
                     │                                │
                     │         MinIO / S3             │
                     │                                │
                     │  RAW → CLEANED → CURATED       │
                     └───────────────┬────────────────┘
                                     │
                                     ▼
                           ┌─────────────────────┐
                           │    APACHE SPARK     │
                           │                     │
                           │ Transformations     │
                           │ Aggregations        │
                           │ Data Processing      │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │    APACHE HUDI      │
                           │     LAKEHOUSE       │
                           └──────────┬──────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
      ┌───────────────┐      ┌────────────────┐      ┌────────────────┐
      │  PostgreSQL   │      │ Elasticsearch  │      │ ML / AI        │
      │               │      │                │      │                │
      │ Analytics     │      │ Search         │      │ Prediction     │
      │ KPIs          │      │ Documents      │      │ NLP / RAG      │
      └───────┬───────┘      └───────┬────────┘      └───────┬────────┘
              │                       │                       │
              └───────────────────────┼───────────────────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │       FastAPI       │
                           │      REST API       │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │       React        │
                           │    Web Platform     │
                           └─────────────────────┘
```

---

## 2. Architecture Layers

### Layer 1 — Sources

External data sources provide heterogeneous information.

Examples:

* OpenAlex API
* Crossref API
* Moroccan university websites
* Public PDF documents
* Public datasets

---

### Layer 2 — Ingestion

Python collectors retrieve data from external sources.

Components:

```text
data-engineering/ingestion/

├── scrapers/
├── api_collectors/
└── pdf_extractors/
```

Responsibilities:

* connection to sources
* extraction
* basic validation
* metadata generation
* error handling
* raw data creation

---

### Layer 3 — Orchestration

Apache Airflow controls the execution of pipelines.

Responsibilities:

* scheduling
* dependencies
* retries
* monitoring
* logging
* failure handling

Example:

```text
extract
   ↓
validate
   ↓
store_raw
   ↓
transform
   ↓
quality_check
   ↓
publish
```

---

### Layer 4 — Data Lake

MinIO provides S3-compatible object storage during local development.

The Data Lake stores the original and processed data.

```text
data-lake/

├── raw/
├── cleaned/
└── curated/
```

The raw layer preserves source data and enables reproducibility.

---

### Layer 5 — Processing

Apache Spark performs distributed data processing.

Responsibilities:

* transformation
* cleaning
* joins
* aggregations
* deduplication
* feature generation
* large-scale processing

---

### Layer 6 — Lakehouse

Apache Hudi provides transactional and incremental capabilities on top of object storage.

Responsibilities:

* managed datasets
* updates
* incremental processing
* schema evolution
* historical data

---

### Layer 7 — Serving

Different consumers require different storage systems.

#### PostgreSQL

Used for:

* analytical datasets
* relational queries
* API queries
* KPI generation

#### Elasticsearch

Used for:

* full-text search
* document search
* university search
* program search

#### ML / AI

Used for:

* predictions
* clustering
* NLP
* recommendations
* RAG

---

### Layer 8 — Application

FastAPI provides the backend REST API.

React provides the frontend.

The frontend communicates with the backend rather than directly accessing internal databases.

---

## 3. Architectural Principles

### Separation of concerns

Each component has a specific responsibility.

### Reproducibility

Raw data must remain available so transformations can be reproduced.

### Scalability

The architecture must support increasing data volumes.

### Observability

Pipelines and services must produce logs and metrics.

### Security

Credentials and secrets must never be hardcoded in source code.

### Modularity

Components should be independently testable and replaceable.

---

## 4. Local Development Architecture

The initial development environment will run locally using Docker.

Expected services:

```text
MinIO
PostgreSQL
Apache Spark
Apache Airflow
Elasticsearch
Metabase
FastAPI
React
Prometheus
Grafana
```

Not every service will be activated immediately.

The platform will be built incrementally.

---

## 5. Cloud Evolution

The local architecture is designed to evolve toward cloud infrastructure.

Example:

```text
LOCAL                         CLOUD

MinIO          ───────────→   Amazon S3
PostgreSQL     ───────────→   Managed PostgreSQL
Docker         ───────────→   Cloud Containers
Terraform      ───────────→   Cloud Infrastructure
Prometheus     ───────────→   Cloud Monitoring
```

The project will first prove the architecture locally before introducing cloud costs.
