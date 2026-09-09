# Data Model

## 1. Objective

The Data Model defines the main entities managed by the Morocco Data Intelligence Platform and their relationships.

The model is designed to support:

* Data Engineering
* Data Analytics
* Data Science
* Machine Learning
* NLP
* Search
* APIs
* Business Intelligence

The model separates source identifiers from platform identifiers to support data integration from multiple sources.

---

# 2. Main Entities

The initial platform contains the following entities:

```text
University
    │
    ├── Faculty
    │      │
    │      └── Program
    │
    ├── Researcher
    │      │
    │      └── Publication
    │
    └── Document
```

---

# 3. University

A university represents a higher-education institution.

### Logical schema

| Field         | Type      | Description                  |
| ------------- | --------- | ---------------------------- |
| university_id | UUID      | Internal platform identifier |
| source_id     | VARCHAR   | Identifier from source       |
| name          | VARCHAR   | Official name                |
| name_ar       | VARCHAR   | Arabic name                  |
| type          | VARCHAR   | University type              |
| city          | VARCHAR   | City                         |
| region        | VARCHAR   | Moroccan region              |
| website       | VARCHAR   | Official website             |
| status        | VARCHAR   | Institution status           |
| source        | VARCHAR   | Data source                  |
| source_url    | VARCHAR   | Source URL                   |
| first_seen_at | TIMESTAMP | First ingestion              |
| last_seen_at  | TIMESTAMP | Last ingestion               |
| updated_at    | TIMESTAMP | Last update                  |

### Primary Key

```text
university_id
```

### Business uniqueness

The platform should attempt to identify a university using a combination of:

```text
normalized_name
+
city
+
website
```

---

# 4. Faculty

A faculty belongs to a university.

### Logical schema

| Field         | Type      | Description         |
| ------------- | --------- | ------------------- |
| faculty_id    | UUID      | Internal identifier |
| university_id | UUID      | Parent university   |
| source_id     | VARCHAR   | Source identifier   |
| name          | VARCHAR   | Faculty name        |
| name_ar       | VARCHAR   | Arabic name         |
| city          | VARCHAR   | City                |
| website       | VARCHAR   | Website             |
| source        | VARCHAR   | Data source         |
| source_url    | VARCHAR   | Source URL          |
| first_seen_at | TIMESTAMP | First ingestion     |
| last_seen_at  | TIMESTAMP | Last ingestion      |

### Primary Key

```text
faculty_id
```

### Foreign Key

```text
university_id → university.university_id
```

---

# 5. Academic Program

A program represents an academic training program.

Examples:

```text
Licence Informatique
Master Big Data
Master Cloud Computing
Doctorat
```

### Logical schema

| Field         | Type      | Description                  |
| ------------- | --------- | ---------------------------- |
| program_id    | UUID      | Internal identifier          |
| university_id | UUID      | University                   |
| faculty_id    | UUID      | Faculty                      |
| source_id     | VARCHAR   | Source identifier            |
| name          | VARCHAR   | Program name                 |
| name_ar       | VARCHAR   | Arabic name                  |
| level         | VARCHAR   | Licence / Master / Doctorate |
| field         | VARCHAR   | Academic field               |
| duration      | INTEGER   | Duration                     |
| duration_unit | VARCHAR   | Year / Semester              |
| description   | TEXT      | Description                  |
| language      | VARCHAR   | Teaching language            |
| website       | VARCHAR   | Program website              |
| source        | VARCHAR   | Data source                  |
| source_url    | VARCHAR   | Source URL                   |
| first_seen_at | TIMESTAMP | First ingestion              |
| last_seen_at  | TIMESTAMP | Last ingestion               |

### Primary Key

```text
program_id
```

### Foreign Keys

```text
university_id → university.university_id

faculty_id → faculty.faculty_id
```

---

# 6. Researcher

A researcher represents an academic or scientific researcher.

### Logical schema

| Field             | Type      | Description            |
| ----------------- | --------- | ---------------------- |
| researcher_id     | UUID      | Internal identifier    |
| source_id         | VARCHAR   | Source identifier      |
| name              | VARCHAR   | Researcher name        |
| institution       | VARCHAR   | Institution            |
| research_field    | VARCHAR   | Main research field    |
| ORCID             | VARCHAR   | ORCID if available     |
| OpenAlex_id       | VARCHAR   | OpenAlex identifier    |
| publication_count | INTEGER   | Number of publications |
| citation_count    | INTEGER   | Citation count         |
| source            | VARCHAR   | Data source            |
| first_seen_at     | TIMESTAMP | First ingestion        |
| last_seen_at      | TIMESTAMP | Last ingestion         |

### Primary Key

```text
researcher_id
```

---

# 7. Publication

A publication represents a scientific publication.

### Logical schema

| Field            | Type      | Description         |
| ---------------- | --------- | ------------------- |
| publication_id   | UUID      | Internal identifier |
| source_id        | VARCHAR   | Source identifier   |
| title            | TEXT      | Publication title   |
| abstract         | TEXT      | Abstract            |
| publication_year | INTEGER   | Publication year    |
| publication_date | DATE      | Publication date    |
| DOI              | VARCHAR   | DOI                 |
| journal          | VARCHAR   | Journal             |
| publisher        | VARCHAR   | Publisher           |
| research_field   | VARCHAR   | Research field      |
| citation_count   | INTEGER   | Citation count      |
| source           | VARCHAR   | Data source         |
| source_url       | VARCHAR   | Source URL          |
| first_seen_at    | TIMESTAMP | First ingestion     |
| last_seen_at     | TIMESTAMP | Last ingestion      |

### Primary Key

```text
publication_id
```

---

# 8. Publication Authors

A publication can have multiple researchers and a researcher can have multiple publications.

Therefore, this is a many-to-many relationship.

An association table will be used:

```text
publication_authors
```

### Schema

| Field                | Type    |
| -------------------- | ------- |
| publication_id       | UUID    |
| researcher_id        | UUID    |
| author_position      | INTEGER |
| corresponding_author | BOOLEAN |

### Composite Primary Key

```text
publication_id
+
researcher_id
```

---

# 9. Document

A document represents an institutional or academic document.

Examples:

```text
Program
Regulation
Report
Announcement
Research document
Course description
```

### Logical schema

| Field               | Type      | Description         |
| ------------------- | --------- | ------------------- |
| document_id         | UUID      | Internal identifier |
| university_id       | UUID      | University          |
| faculty_id          | UUID      | Faculty             |
| title               | TEXT      | Document title      |
| document_type       | VARCHAR   | Type                |
| language            | VARCHAR   | Language            |
| file_type           | VARCHAR   | PDF / DOCX / HTML   |
| file_size           | BIGINT    | Size in bytes       |
| source_url          | VARCHAR   | Source URL          |
| storage_path        | VARCHAR   | Data Lake path      |
| text                | TEXT      | Extracted text      |
| extraction_quality  | DOUBLE    | Extraction quality  |
| needs_ocr           | BOOLEAN   | OCR required        |
| publication_date    | DATE      | Publication date    |
| ingestion_timestamp | TIMESTAMP | Ingestion time      |
| updated_at          | TIMESTAMP | Update time         |

### Primary Key

```text
document_id
```

---

# 10. Relationships

The main relationships are:

```text
University
    │
    │ 1:N
    ▼
Faculty
    │
    │ 1:N
    ▼
Program
```

And:

```text
Researcher
    │
    │ N:M
    ▼
Publication
```

Through:

```text
publication_authors
```

Documents are linked to institutions:

```text
University
    │
    │ 1:N
    ▼
Document
```

and optionally:

```text
Faculty
    │
    │ 1:N
    ▼
Document
```

---

# 11. Entity Relationship Model

```text
                         ┌─────────────────┐
                         │    UNIVERSITY   │
                         │─────────────────│
                         │ PK university_id│
                         │ name            │
                         │ city            │
                         │ region          │
                         └────────┬────────┘
                                  │
                         1        │       N
                                  │
                         ┌────────▼────────┐
                         │     FACULTY     │
                         │─────────────────│
                         │ PK faculty_id   │
                         │ FK university_id│
                         │ name            │
                         └────────┬────────┘
                                  │
                         1        │       N
                                  │
                         ┌────────▼────────┐
                         │     PROGRAM     │
                         │─────────────────│
                         │ PK program_id   │
                         │ FK faculty_id   │
                         │ FK university_id│
                         │ name            │
                         │ level           │
                         │ field           │
                         └─────────────────┘


┌─────────────────┐       ┌────────────────────┐       ┌─────────────────┐
│   RESEARCHER    │       │ PUBLICATION_AUTHORS│       │   PUBLICATION   │
│─────────────────│       │────────────────────│       │─────────────────│
│PK researcher_id │◄──────│FK researcher_id   │──────►│PK publication_id│
│name             │   N:1 │FK publication_id  │  1:N  │title            │
│research_field   │       │author_position    │       │DOI              │
│ORCID            │       └────────────────────┘       │year             │
└─────────────────┘                                   │citations        │
                                                      └─────────────────┘


                         ┌─────────────────┐
                         │    DOCUMENT     │
                         │─────────────────│
                         │ PK document_id  │
                         │ FK university_id│
                         │ FK faculty_id   │
                         │ title           │
                         │ document_type   │
                         │ language        │
                         │ storage_path    │
                         │ extracted_text  │
                         └─────────────────┘
```

---

# 12. Source Identity vs Platform Identity

The platform distinguishes between:

### Internal identity

```text
university_id
faculty_id
program_id
publication_id
document_id
```

and:

### External identity

```text
source_id
OpenAlex_id
DOI
ORCID
source_url
```

This prevents external identifiers from becoming tightly coupled to the internal data model.

---

# 13. Data Integration

The same entity may appear in multiple sources.

Example:

```text
Source A:
Université Hassan II

Source B:
Hassan II University

Source C:
Université Hassan II de Casablanca
```

The platform must normalize these representations and attempt entity resolution.

Potential techniques:

* string normalization
* accent normalization
* lowercase conversion
* URL comparison
* exact matching
* fuzzy matching
* manual validation for ambiguous cases

---

# 14. Slowly Changing Data

Important institutional attributes may change over time.

Examples:

```text
University name
Website
Program status
Program description
```

The Lakehouse should preserve historical versions where appropriate.

---

# 15. Metadata

Every major dataset should contain metadata.

Minimum metadata:

```text
source
source_url
ingestion_timestamp
pipeline_id
schema_version
record_hash
```

This allows data lineage and reproducibility.

---

# 16. Data Lineage

The platform should be able to trace:

```text
Original Source
      ↓
Raw Object
      ↓
Transformation
      ↓
Curated Dataset
      ↓
Analytics Table
      ↓
Dashboard / ML Model / API
```

---

# 17. Data Model Evolution

The schema is expected to evolve as new sources and use cases are discovered.

Schema evolution must be documented through Architecture Decision Records.

Changes should not silently break downstream pipelines.

---

# 18. Initial Core Tables

The first implementation will focus on:

```text
universities
faculties
programs
researchers
publications
publication_authors
documents
```

Additional tables may be introduced when justified by a concrete use case.

---

# 19. Design Principle

The data model should remain:

* understandable
* normalized where appropriate
* scalable
* traceable
* source-independent
* compatible with analytics
* compatible with machine learning
* compatible with APIs
