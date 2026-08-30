# Morocco Data Intelligence Platform

## Project Specification

**Project name:** Morocco Data Intelligence Platform
**Short name:** EduData Morocco
**Version:** 1.0
**Status:** Planning / Architecture Phase
**Author:** Zineb Hamouchi

---

# 1. Executive Summary

Morocco Data Intelligence Platform is an end-to-end Big Data and Artificial Intelligence platform designed to collect, process, store, analyze and expose heterogeneous data related to Moroccan universities, academic programs, scientific publications and institutional documents.

The platform combines Data Engineering, Big Data, Data Analytics, Data Science, Machine Learning, NLP, Artificial Intelligence, Software Engineering, Cloud Computing and DevOps.

The objective is to build a production-oriented portfolio project demonstrating the complete data lifecycle:

```text
Data Sources
     ↓
Data Ingestion
     ↓
Data Lake
     ↓
Data Processing
     ↓
Lakehouse
     ↓
Data Quality
     ↓
Analytics
     ↓
Machine Learning / AI
     ↓
APIs
     ↓
Web Application
     ↓
Cloud Deployment
```

---

# 2. Business Problem

University and scientific information is distributed across multiple heterogeneous sources:

* university websites
* institutional websites
* scientific APIs
* public datasets
* PDF documents
* research metadata
* structured and semi-structured files

These sources may contain different schemas, formats, naming conventions and levels of data quality.

This makes it difficult to obtain a centralized and reliable view of the Moroccan higher-education ecosystem.

The platform aims to solve this problem by building a unified data platform capable of:

* collecting heterogeneous data
* standardizing information
* detecting data quality issues
* storing historical data
* processing large datasets
* generating analytical indicators
* supporting machine learning
* providing search capabilities
* exposing data through APIs
* providing an interactive user interface

---

# 3. Project Objectives

## 3.1 Main Objectives

The project aims to:

1. Build a reliable data ingestion architecture.
2. Implement a Data Lake using object storage.
3. Implement a Lakehouse architecture.
4. Process data using Apache Spark.
5. Orchestrate pipelines using Apache Airflow.
6. Implement automated data-quality checks.
7. Build analytical datasets using PostgreSQL.
8. Create BI dashboards.
9. Perform exploratory data analysis.
10. Develop machine-learning models.
11. Implement NLP capabilities for documents.
12. Implement search using Elasticsearch.
13. Develop a REST API using FastAPI.
14. Develop a web application using React.
15. Containerize the platform using Docker.
16. Implement CI/CD using GitHub Actions.
17. Deploy selected components to a Cloud environment.
18. Implement monitoring and logging.

---

# 4. Target Users

## 4.1 Data Engineer

Responsibilities:

* monitor ingestion pipelines
* validate data quality
* maintain transformations
* monitor Spark jobs
* manage storage layers

## 4.2 Data Analyst

Needs:

* KPIs
* dashboards
* SQL analytics
* historical trends
* university comparisons

## 4.3 Data Scientist

Needs:

* analytical datasets
* machine-learning features
* historical data
* statistical analysis
* model evaluation

## 4.4 Researcher

Needs:

* scientific publications
* research fields
* university research activity
* document search

## 4.5 Student

Needs:

* university search
* academic program search
* program information
* recommendations

## 4.6 Platform Administrator

Needs:

* user management
* system monitoring
* pipeline monitoring
* access control

---

# 5. Data Domains

The platform will initially focus on the following domains.

## 5.1 Universities

Example attributes:

```text
university_id
name
name_ar
type
city
region
website
status
source
last_updated
```

## 5.2 Faculties

```text
faculty_id
university_id
name
name_ar
city
website
source
last_updated
```

## 5.3 Academic Programs

```text
program_id
university_id
faculty_id
name
level
field
duration
description
source
last_updated
```

## 5.4 Scientific Publications

```text
publication_id
title
authors
year
doi
journal
publisher
research_field
institution
citation_count
source
```

## 5.5 Researchers

```text
researcher_id
name
institution
research_field
publication_count
citation_count
source
```

## 5.6 Documents

```text
document_id
title
document_type
university
faculty
source_url
language
publication_date
file_type
file_size
text
extraction_quality
```

---

# 6. Data Sources

The platform will use several categories of sources.

## 6.1 Scientific APIs

Potential sources:

* OpenAlex
* Crossref

These sources will primarily provide scientific publication metadata.

## 6.2 University Websites

Web scraping will be used where appropriate and permitted to collect publicly available information.

Possible data:

* universities
* faculties
* programs
* departments
* institutional information

## 6.3 PDF Documents

Potential documents:

* academic programs
* regulations
* institutional reports
* research documents
* public announcements

## 6.4 Public Datasets

Public datasets may be integrated when their licensing and usage conditions permit.

---

# 7. Data Architecture

The platform will follow a layered Data Lakehouse architecture.

```text
                         DATA SOURCES
                              │
              ┌───────────────┼───────────────┐
              │               │               │
             APIs          Websites          PDFs
              │               │               │
              └───────────────┼───────────────┘
                              │
                              ▼
                         INGESTION
                              │
                     Python / Collectors
                              │
                              ▼
                          AIRFLOW
                              │
                              ▼
                       DATA LAKE / RAW
                         MinIO / S3
                              │
                              ▼
                        APACHE SPARK
                              │
                  ┌───────────┴───────────┐
                  │                       │
                  ▼                       ▼
               CLEANED                 CURATED
                  │                       │
                  └───────────┬───────────┘
                              ▼
                         APACHE HUDI
                          LAKEHOUSE
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        PostgreSQL       Elasticsearch       ML
             │                │                │
             ▼                ▼                ▼
        Analytics           Search         Predictions
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                           FastAPI
                              │
                              ▼
                           React
                              │
                              ▼
                            Users
```

---

# 8. Storage Layers

## 8.1 Raw Layer

Contains data as close as possible to the original source.

Examples:

```text
raw/
├── universities/
├── faculties/
├── programs/
├── publications/
└── documents/
```

No destructive transformation should be performed in this layer.

---

## 8.2 Cleaned Layer

Data is:

* parsed
* normalized
* cleaned
* deduplicated
* type-converted
* validated

---

## 8.3 Curated Layer

The curated layer contains datasets optimized for analytics and downstream applications.

Example tables:

```text
universities
faculties
programs
publications
researchers
documents
```

---

# 9. Data Engineering Requirements

The platform must support:

* batch ingestion
* API ingestion
* web scraping
* document ingestion
* schema validation
* data normalization
* deduplication
* incremental processing
* error handling
* logging
* pipeline retries
* pipeline monitoring

---

# 10. Orchestration

Apache Airflow will orchestrate the data pipelines.

Example pipeline:

```text
START
  ↓
Collect Universities
  ↓
Validate Raw Data
  ↓
Store Raw Data
  ↓
Transform Data
  ↓
Validate Curated Data
  ↓
Update Lakehouse
  ↓
Load Analytics Database
  ↓
END
```

Future pipelines:

```text
University ingestion
Publication ingestion
Document ingestion
Transformation
Data quality
Search indexing
ML feature generation
```

---

# 11. Big Data Processing

Apache Spark will be used for distributed processing.

The project will demonstrate:

* DataFrames
* Spark SQL
* joins
* aggregations
* window functions
* partitioning
* caching
* handling of large datasets
* performance optimization

Performance experiments may compare:

```text
Pandas
vs
PySpark
```

for appropriate workloads.

---

# 12. Lakehouse

Apache Hudi will be used to implement Lakehouse tables.

The project will demonstrate:

* table creation
* schema evolution
* record updates
* incremental processing
* partitioning
* historical data management

The Lakehouse will act as the central analytical storage layer.

---

# 13. Data Quality

Data quality is a core component of the platform.

The system will implement checks for:

### Completeness

```text
NULL values
Missing attributes
```

### Uniqueness

```text
Duplicate universities
Duplicate publications
Duplicate documents
```

### Validity

```text
Invalid dates
Invalid URLs
Invalid data types
Invalid categorical values
```

### Consistency

```text
Foreign-key relationships
University / faculty relationships
Program / faculty relationships
```

### Freshness

The system will monitor when datasets were last updated.

---

# 14. Data Analytics

The analytical layer will use PostgreSQL.

The platform will provide KPIs such as:

```text
Total universities
Total faculties
Total academic programs
Total publications
Total researchers
Total documents
```

Additional indicators:

```text
Publications by year
Publications by university
Programs by field
Programs by region
Research activity by institution
Document quality indicators
```

---

# 15. Business Intelligence

Metabase will provide interactive dashboards.

Initial dashboards:

## Dashboard 1 — University Overview

* number of universities
* universities by region
* universities by type
* number of faculties
* number of programs

## Dashboard 2 — Research Analytics

* publications by year
* publications by institution
* research fields
* publication trends

## Dashboard 3 — Education Analytics

* programs by field
* programs by academic level
* programs by university

## Dashboard 4 — Data Quality

* missing values
* duplicates
* validation failures
* extraction quality

---

# 16. Data Science

The Data Science layer will include:

```text
Data preparation
       ↓
Exploratory Data Analysis
       ↓
Statistical analysis
       ↓
Feature engineering
       ↓
Model training
       ↓
Model evaluation
       ↓
Prediction
```

Techniques may include:

* descriptive statistics
* correlation analysis
* PCA
* clustering
* classification
* regression

---

# 17. Machine Learning Use Cases

## 17.1 Program Demand Prediction

The platform may estimate future demand for academic programs using historical and contextual features.

Possible features:

```text
year
university
field
academic level
historical demand
region
number of programs
```

Output:

```text
Predicted demand
```

---

## 17.2 University Clustering

Universities may be grouped according to their academic and research characteristics.

Possible methodology:

```text
Feature engineering
        ↓
Normalization
        ↓
PCA
        ↓
K-Means
        ↓
Cluster analysis
```

---

# 18. NLP

The NLP layer will process university documents.

Potential tasks:

* text extraction
* language detection
* document classification
* keyword extraction
* named entity recognition
* information extraction

Possible document categories:

```text
Program
Course
Regulation
Research
Announcement
Report
```

---

# 19. AI Assistant

A future RAG-based assistant will allow users to ask questions about indexed university documents.

Example:

```text
User question
      ↓
Query processing
      ↓
Document retrieval
      ↓
Relevant context
      ↓
LLM
      ↓
Answer
```

The assistant must rely on retrieved sources rather than generating unsupported university information.

---

# 20. Search Engine

Elasticsearch will provide full-text search.

Searchable entities:

```text
Universities
Faculties
Programs
Publications
Researchers
Documents
```

The search layer may support:

* full-text search
* filters
* ranking
* autocomplete
* entity-specific search

---

# 21. Backend

FastAPI will expose the platform through REST APIs.

Initial endpoints may include:

```text
GET /universities
GET /universities/{id}

GET /faculties
GET /programs
GET /publications
GET /researchers
GET /documents

GET /search

GET /analytics
GET /analytics/universities
GET /analytics/publications

POST /predictions
POST /recommendations
```

The API will later include:

* authentication
* authorization
* validation
* error handling
* logging
* API documentation

---

# 22. Frontend

React will provide the user interface.

Main sections:

```text
Dashboard
Universities
Faculties
Programs
Publications
Researchers
Documents
Search
Analytics
Predictions
AI Assistant
```

The interface should consume the FastAPI backend rather than directly accessing databases.

---

# 23. Security

Security requirements include:

* environment variables for secrets
* no credentials committed to Git
* authentication
* authorization
* role-based access control
* API input validation
* secure configuration
* dependency management

Possible roles:

```text
ADMIN
ANALYST
RESEARCHER
STUDENT
```

---

# 24. DevOps

The project will use Docker to ensure reproducibility.

The development environment will progressively containerize:

```text
MinIO
PostgreSQL
Spark
Airflow
Elasticsearch
Metabase
FastAPI
React
```

GitHub Actions will later implement:

```text
Git Push
   ↓
Lint
   ↓
Unit Tests
   ↓
Integration Tests
   ↓
Build
   ↓
Security Checks
   ↓
Deployment
```

---

# 25. Cloud Strategy

The platform will initially be developed locally.

After the local architecture becomes stable, selected services will be migrated to a Cloud environment.

Possible technologies:

```text
Object Storage → Amazon S3
Compute → EC2 / managed compute
Database → PostgreSQL managed service
Monitoring → Cloud monitoring
Infrastructure → Terraform
```

The final Cloud architecture will depend on cost, educational objectives and available resources.

---

# 26. Monitoring

The monitoring layer will track:

* pipeline failures
* pipeline duration
* API latency
* system resources
* Spark jobs
* Airflow DAGs
* database health
* application errors

Potential technologies:

```text
Prometheus
Grafana
Application logging
```

---

# 27. Testing Strategy

The project will implement several levels of testing.

## Unit Tests

Test individual functions.

```text
scrapers
transformations
validators
API functions
ML preprocessing
```

## Integration Tests

Test interactions between components.

Examples:

```text
Python → MinIO
Spark → Hudi
Spark → PostgreSQL
FastAPI → PostgreSQL
FastAPI → Elasticsearch
```

## Data Tests

Validate:

```text
schema
nulls
duplicates
relationships
data types
```

---

# 28. Repository Structure

```text
morocco-data-intelligence-platform/

├── .github/
│   └── workflows/
│
├── docs/
│   ├── architecture/
│   ├── decision-records/
│   ├── guides/
│   ├── project-specification.md
│   └── README.md
│
├── data-engineering/
│   ├── common/
│   ├── ingestion/
│   ├── transformations/
│   ├── quality/
│   └── README.md
│
├── airflow/
├── spark/
├── lakehouse/
├── analytics/
├── data-science/
├── nlp/
├── ai/
├── backend/
├── frontend/
├── elasticsearch/
├── dashboards/
├── infrastructure/
├── monitoring/
├── tests/
├── scripts/
└── config/
```

---

# 29. Development Roadmap

## Milestone 0 — Specification

```text
Project specification
Architecture
Data model
Technology decisions
```

## Milestone 1 — Data Engineering MVP

```text
Data sources
Python ingestion
MinIO
Basic validation
```

## Milestone 2 — Orchestration

```text
Airflow
DAGs
Retries
Logging
Scheduling
```

## Milestone 3 — Big Data

```text
Spark
Transformations
Hudi
Lakehouse
```

## Milestone 4 — Data Quality

```text
Validation
Data profiling
Quality metrics
Tests
```

## Milestone 5 — Analytics

```text
PostgreSQL
SQL
KPIs
Metabase
```

## Milestone 6 — Data Science

```text
EDA
Statistics
Feature engineering
ML
Evaluation
```

## Milestone 7 — AI/NLP

```text
Document processing
NLP
Search
RAG assistant
```

## Milestone 8 — Application

```text
FastAPI
React
Authentication
Search
Dashboards
```

## Milestone 9 — Cloud & DevOps

```text
Docker
Cloud
Terraform
GitHub Actions
Monitoring
```

---

# 30. Definition of Done

The project will be considered production-oriented when:

* data can be ingested automatically
* pipelines are orchestrated
* data is stored in a Lakehouse
* transformations are reproducible
* data quality is measured
* analytical datasets are available
* dashboards provide meaningful KPIs
* ML models have documented evaluation results
* documents can be searched
* APIs expose platform functionality
* frontend consumes the APIs
* services are containerized
* tests are automated
* CI/CD is implemented
* monitoring is available
* documentation is complete
* the complete system can be reproduced from the repository

---

# 31. Current Status

```text
[✓] Repository created
[✓] Project structure created
[✓] Initial README
[✓] Git configuration
[✓] Environment template
[✓] Initial prototype files

[ ] Project specification
[ ] Architecture documentation
[ ] Data contracts
[ ] Data sources
[ ] Production ingestion
[ ] Data Lake
[ ] Spark
[ ] Hudi
[ ] Data Quality
[ ] Analytics
[ ] Machine Learning
[ ] NLP
[ ] AI Assistant
[ ] Backend
[ ] Frontend
[ ] Cloud
[ ] CI/CD
[ ] Monitoring
```

---

# 32. Project Principles

The project will follow these principles:

1. **Build incrementally.**
2. **Prefer reproducibility over shortcuts.**
3. **Separate raw, cleaned and curated data.**
4. **Treat data quality as a first-class concern.**
5. **Document architectural decisions.**
6. **Test important components.**
7. **Never commit secrets.**
8. **Use Git commits with meaningful messages.**
9. **Prefer production-like practices over notebook-only solutions.**
10. **Every major technology must have a concrete purpose.**
