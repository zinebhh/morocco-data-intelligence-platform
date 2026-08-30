# Data Flow Architecture

## 1. End-to-End Data Flow

The platform follows an end-to-end data lifecycle:

```text
External Sources
      │
      ▼
Extraction
      │
      ▼
Raw Data
      │
      ▼
Data Validation
      │
      ▼
Data Cleaning
      │
      ▼
Transformation
      │
      ▼
Lakehouse
      │
      ├──────────────► Analytics
      │
      ├──────────────► Search
      │
      └──────────────► Machine Learning
                              │
                              ▼
                           AI / NLP
                              │
                              ▼
                         Application
```

---

# 2. Ingestion Flow

Each ingestion pipeline follows this process:

```text
SOURCE
  ↓
CONNECT
  ↓
EXTRACT
  ↓
VALIDATE
  ↓
ADD METADATA
  ↓
STORE RAW
```

Every ingestion should generate metadata such as:

```text
source
source_url
ingestion_timestamp
pipeline_id
dataset
format
schema_version
```

---

# 3. Transformation Flow

The transformation pipeline follows:

```text
RAW
 ↓
READ
 ↓
PARSE
 ↓
CLEAN
 ↓
NORMALIZE
 ↓
DEDUPLICATE
 ↓
VALIDATE
 ↓
WRITE CLEANED
 ↓
CURATE
```

---

# 4. Data Quality Flow

Quality checks occur before publishing analytical data.

```text
Dataset
   ↓
Schema Validation
   ↓
Completeness Check
   ↓
Uniqueness Check
   ↓
Validity Check
   ↓
Consistency Check
   ↓
Freshness Check
   ↓
Quality Score
```

If critical checks fail, the pipeline should not publish the dataset.

---

# 5. Analytics Flow

```text
Curated Lakehouse
       ↓
Spark / SQL
       ↓
PostgreSQL
       ↓
Metabase
       ↓
Business KPIs
```

---

# 6. Machine Learning Flow

```text
Curated Data
      ↓
Feature Engineering
      ↓
Training Dataset
      ↓
Train / Validation / Test
      ↓
Model Training
      ↓
Evaluation
      ↓
Model Registry
      ↓
Prediction API
```

---

# 7. NLP / RAG Flow

```text
PDF / Document
      ↓
Text Extraction
      ↓
Cleaning
      ↓
Chunking
      ↓
Embeddings
      ↓
Vector Index
      ↓
Retrieval
      ↓
Relevant Context
      ↓
LLM
      ↓
Answer
```

The assistant should provide references to the retrieved documents whenever possible.

---

# 8. Application Flow

```text
User
 ↓
React
 ↓
FastAPI
 ↓
Authentication
 ↓
Business Logic
 ↓
PostgreSQL / Elasticsearch / ML
 ↓
Response
 ↓
React
```
