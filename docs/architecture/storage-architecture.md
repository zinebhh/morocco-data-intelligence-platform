# Storage Architecture

## 1. Storage Strategy

The platform uses a multi-layer storage architecture.

```text
                 OBJECT STORAGE
                      │
                      ▼
             ┌──────────────────┐
             │       RAW        │
             │ Original Sources │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │     CLEANED      │
             │ Standardized     │
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │     CURATED      │
             │ Business-ready   │
             └────────┬─────────┘
                      │
              ┌───────┼────────┐
              ▼       ▼        ▼
           SQL DB  Search      ML
```

---

# 2. Raw Layer

The raw layer contains source data with minimal modification.

Example:

```text
raw/
├── universities/
│   └── 2026/
├── publications/
│   └── 2026/
├── programs/
│   └── 2026/
└── documents/
    └── 2026/
```

Raw data should be immutable whenever possible.

---

# 3. Cleaned Layer

The cleaned layer contains:

* normalized values
* standardized schemas
* corrected types
* removed duplicates
* validated records

Example:

```text
cleaned/
├── universities/
├── faculties/
├── programs/
├── publications/
└── documents/
```

---

# 4. Curated Layer

The curated layer contains business-ready datasets.

Example:

```text
curated/
├── universities/
├── faculties/
├── programs/
├── publications/
├── researchers/
└── documents/
```

These datasets are consumed by analytics and machine-learning workloads.

---

# 5. Partitioning Strategy

Datasets will be partitioned when useful.

Potential partition keys:

```text
year
region
university_id
document_type
```

Partitioning decisions will be based on query patterns and dataset size rather than applied blindly.

---

# 6. File Formats

The platform may use:

### JSON

For raw API responses and semi-structured data.

### CSV

For simple exchange and testing.

### Parquet

For analytical datasets because it is column-oriented and efficient.

### Hudi

For managed Lakehouse tables.

---

# 7. PostgreSQL

PostgreSQL is the relational serving layer.

It will contain analytical tables and API-facing datasets.

Example:

```text
universities
faculties
programs
publications
researchers
documents
```

---

# 8. Elasticsearch

Elasticsearch is optimized for search workloads.

It will index:

```text
universities
programs
publications
documents
```

Search is separated from transactional and analytical workloads.

---

# 9. Data Retention

Raw historical data should be retained according to the project's storage constraints.

The architecture must allow historical reconstruction of datasets.

---

# 10. Storage Security

Credentials must be provided through environment variables or secret-management mechanisms.

No credentials should be committed to Git.
