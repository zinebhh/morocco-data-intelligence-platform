# Deployment Architecture

## 1. Development Environment

The initial platform runs locally.

```text
Windows
   │
   ├── VS Code
   ├── Git
   ├── Python
   ├── Docker Desktop
   │
   └── Docker Compose
          │
          ├── MinIO
          ├── PostgreSQL
          ├── Airflow
          ├── Spark
          ├── Elasticsearch
          ├── Metabase
          ├── FastAPI
          └── React
```

Services will be introduced progressively.

---

# 2. Containerization

Each major service should run in an isolated container.

Benefits:

* reproducibility
* dependency isolation
* easier deployment
* consistent development environment
* easier testing

---

# 3. Production Evolution

The target architecture is cloud-ready.

```text
                         CLOUD
                           │
              ┌────────────┴────────────┐
              │                         │
         Object Storage             Compute
              │                         │
              ▼                         ▼
          Amazon S3              Containers / VMs
              │                         │
              ├──────────────┬──────────┤
              │              │
              ▼              ▼
        Managed DB       Search Service
              │
              ▼
           FastAPI
              │
              ▼
            React
```

---

# 4. Infrastructure as Code

Terraform will be introduced after the local architecture is stable.

Terraform will manage infrastructure resources in a reproducible way.

---

# 5. CI/CD

GitHub Actions will automate:

```text
Push
 ↓
Lint
 ↓
Unit Tests
 ↓
Integration Tests
 ↓
Build Docker Images
 ↓
Security Checks
 ↓
Deploy
```

---

# 6. Monitoring

Production services will expose metrics and logs.

Target architecture:

```text
Applications
     │
     ▼
Metrics / Logs
     │
     ▼
Prometheus
     │
     ▼
Grafana
```

---

# 7. Deployment Principle

The project will follow:

```text
Local
  ↓
Docker
  ↓
CI
  ↓
Staging
  ↓
Cloud
  ↓
Production
```

Cloud deployment will only be introduced after the local system is functional and tested.
