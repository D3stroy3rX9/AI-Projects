# UML Diagrams - Sentiment Analysis System

This document contains UML diagrams describing the system architecture, data flow, and component interactions. Diagrams use Mermaid syntax and can be rendered in GitHub, VS Code, or online tools like [Mermaid Live](https://mermaid.live).

---

## 1. System Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
    end

    subgraph "Frontend Layer"
        NextJS[Next.js App<br/>Port 3000]
    end

    subgraph "API Layer"
        FastAPI[FastAPI Server<br/>Port 8000]
        MLPredictor[ML Predictor<br/>TF-IDF + Naive Bayes]
    end

    subgraph "Worker Layer"
        CeleryWorker[Celery Worker]
        CeleryBeat[Celery Beat<br/>Scheduler]
    end

    subgraph "Data Layer"
        PostgreSQL[PostgreSQL<br/>TimescaleDB<br/>Port 5432]
        Redis[Redis<br/>Port 6379]
    end

    subgraph "Observability Layer"
        Prometheus[Prometheus<br/>Port 9090]
        Jaeger[Jaeger<br/>Port 16686]
        Grafana[Grafana<br/>Port 3001]
    end

    Browser -->|HTTP| NextJS
    NextJS -->|REST API| FastAPI
    FastAPI -->|Predict| MLPredictor
    FastAPI -->|Store| PostgreSQL
    FastAPI -->|Queue Tasks| Redis
    FastAPI -->|Metrics| Prometheus
    FastAPI -->|Traces| Jaeger

    CeleryWorker -->|Consume| Redis
    CeleryWorker -->|Read/Write| PostgreSQL
    CeleryBeat -->|Schedule| Redis

    Prometheus -->|Scrape| FastAPI
    Grafana -->|Query| Prometheus
    Jaeger -->|Collect| FastAPI

    style FastAPI fill:#4CAF50
    style NextJS fill:#61DAFB
    style PostgreSQL fill:#336791
    style MLPredictor fill:#FF9800
```

---

## 2. Sequence Diagram - Sentiment Analysis Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Next.js Frontend
    participant API as FastAPI Backend
    participant ML as ML Predictor
    participant DB as PostgreSQL

    User->>Frontend: Enter text & click "Analyze"
    Frontend->>API: POST /analyze {text: "..."}

    API->>API: Validate input (Pydantic)
    API->>ML: predictor.predict(text)

    ML->>ML: 1. Preprocess text
    ML->>ML: 2. TF-IDF vectorization
    ML->>ML: 3. Naive Bayes prediction
    ML->>ML: 4. Calculate confidence
    ML-->>API: {label, scores, confidence}

    API->>DB: Check if text_hash exists
    DB-->>API: Not found

    API->>DB: INSERT INTO analysis
    DB-->>API: Success

    API-->>Frontend: JSON response
    Frontend->>Frontend: Update UI with results
    Frontend->>API: GET /stats
    API->>DB: Query analytics
    DB-->>API: {total, avg, f1}
    API-->>Frontend: Stats data
    Frontend->>Frontend: Update dashboard cards
    Frontend-->>User: Display results + stats
```

---

## 3. Class Diagram - Database Models

```mermaid
classDiagram
    class Analysis {
        +int id
        +string text_hash
        +string text
        +JSONB sentiment_scores
        +JSONB emotion_scores
        +SentimentLabel predicted_label
        +float confidence
        +DateTime analyzed_at
        +SourceEnum source
        +JSONB extra_metadata
        +__repr__() string
    }

    class Model {
        +int id
        +string name
        +string version
        +string algorithm
        +float f1_score
        +int training_samples
        +int vocabulary_size
        +DateTime created_at
        +bool is_active
        +string model_path
        +JSONB metrics
        +__repr__() string
    }

    class TrainingData {
        +int id
        +string text
        +SentimentLabel label
        +string source
        +DateTime created_at
        +bool used_in_training
        +__repr__() string
    }

    class AnalyticsSummary {
        +int id
        +DateTime date
        +int hour
        +float sentiment_avg
        +int positive_count
        +int neutral_count
        +int negative_count
        +int total_count
        +__repr__() string
    }

    class SentimentLabelEnum {
        <<enumeration>>
        POSITIVE
        NEUTRAL
        NEGATIVE
    }

    class SourceEnum {
        <<enumeration>>
        API
        BATCH
        WEBHOOK
    }

    Analysis --> SentimentLabelEnum
    Analysis --> SourceEnum
    TrainingData --> SentimentLabelEnum
    Model "1" -- "0..*" Analysis : predicts using
    TrainingData "0..*" -- "1" Model : trains
    Analysis "0..*" -- "1" AnalyticsSummary : aggregates into
```

---

## 4. Component Diagram - ML Pipeline

```mermaid
graph LR
    subgraph "ML Pipeline (packages/ml/)"
        Preprocessor[Text Preprocessor<br/>- Remove URLs<br/>- Lowercase<br/>- Clean special chars]

        Trainer[Model Trainer<br/>- TF-IDF Vectorizer<br/>- Multinomial NB<br/>- Train/test split]

        Evaluator[Model Evaluator<br/>- Accuracy<br/>- Precision/Recall<br/>- F1 Score<br/>- Confusion Matrix]

        Predictor[Sentiment Predictor<br/>- Load model<br/>- Preprocess<br/>- Predict<br/>- Explain]
    end

    TrainingData[(Training Data<br/>Database)]
    ModelFile[Model File<br/>.joblib]

    TrainingData -->|texts, labels| Preprocessor
    Preprocessor -->|cleaned texts| Trainer
    Trainer -->|trained model| ModelFile
    Trainer -->|predictions| Evaluator
    Evaluator -->|metrics| ModelFile

    ModelFile -->|load| Predictor
    InputText[User Input] -->|text| Preprocessor
    Preprocessor -->|cleaned| Predictor
    Predictor -->|sentiment| OutputResult[Prediction Result]

    style Trainer fill:#FF9800
    style Predictor fill:#4CAF50
    style Evaluator fill:#2196F3
    style Preprocessor fill:#9C27B0
```

---

## 5. Activity Diagram - Model Training Workflow

```mermaid
flowchart TD
    Start([Start Training]) --> CheckData{Training Data<br/>Available?}

    CheckData -->|No| Error1[Error: No training data]
    CheckData -->|Yes| LoadData[Load training data<br/>from database]

    LoadData --> ExtractData[Extract texts & labels]
    ExtractData --> CheckSize{Enough samples?<br/>>100}

    CheckSize -->|No| Error2[Warning: Small dataset]
    CheckSize -->|Yes| Preprocess[Preprocess all texts]
    Error2 --> Preprocess

    Preprocess --> Split[Train/Test Split<br/>80/20]
    Split --> Vectorize[TF-IDF Vectorization<br/>max_features=5000<br/>ngrams=1-2]

    Vectorize --> Train[Train Naive Bayes<br/>alpha=0.1]
    Train --> Predict[Predict on test set]

    Predict --> Evaluate[Calculate Metrics<br/>Accuracy, F1, etc.]
    Evaluate --> CheckF1{F1 Score > 0.5?}

    CheckF1 -->|No| LowAccuracy[Warning: Low accuracy<br/>Need more data]
    CheckF1 -->|Yes| SaveModel[Save model to .joblib]
    LowAccuracy --> SaveModel

    SaveModel --> SaveDB[Save metadata to DB<br/>Mark as active model]
    SaveDB --> Deactivate[Deactivate old models]

    Deactivate --> Success([Training Complete])
    Error1 --> End([End])
    Success --> End

    style Train fill:#FF9800
    style SaveModel fill:#4CAF50
    style Error1 fill:#f44336
    style Error2 fill:#FF9800
    style LowAccuracy fill:#FF9800
```

---

## 6. Deployment Diagram - Production Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[NGINX/ALB]
    end

    subgraph "Application Tier"
        API1[FastAPI Instance 1]
        API2[FastAPI Instance 2]
        API3[FastAPI Instance N]
    end

    subgraph "Worker Tier"
        Worker1[Celery Worker 1]
        Worker2[Celery Worker 2]
        Beat[Celery Beat]
    end

    subgraph "Frontend Tier"
        Next1[Next.js Instance 1]
        Next2[Next.js Instance 2]
    end

    subgraph "Data Tier"
        PG_Primary[(PostgreSQL<br/>Primary)]
        PG_Replica1[(PostgreSQL<br/>Read Replica 1)]
        PG_Replica2[(PostgreSQL<br/>Read Replica 2)]
        RedisCluster[(Redis Cluster)]
    end

    subgraph "Storage"
        S3[Object Storage<br/>S3/GCS<br/>Model Files]
    end

    subgraph "Monitoring"
        PromServer[Prometheus]
        GrafanaServer[Grafana]
        JaegerServer[Jaeger]
    end

    Users[Users] --> LB
    LB --> Next1
    LB --> Next2

    Next1 --> API1
    Next2 --> API2
    API1 --> PG_Primary
    API2 --> PG_Primary
    API3 --> PG_Primary

    API1 --> PG_Replica1
    API2 --> PG_Replica2

    API1 --> RedisCluster
    API2 --> RedisCluster
    API3 --> RedisCluster

    Worker1 --> RedisCluster
    Worker2 --> RedisCluster
    Beat --> RedisCluster

    Worker1 --> PG_Primary
    Worker2 --> PG_Primary

    API1 --> S3
    API2 --> S3
    Worker1 --> S3

    API1 -.->|metrics| PromServer
    API2 -.->|metrics| PromServer
    API1 -.->|traces| JaegerServer

    PromServer --> GrafanaServer

    PG_Primary -.->|replication| PG_Replica1
    PG_Primary -.->|replication| PG_Replica2

    style PG_Primary fill:#336791
    style RedisCluster fill:#DC382D
    style S3 fill:#569A31
```

---

## 7. State Diagram - Analysis Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Submitted: User submits text

    Submitted --> Validating: API receives request
    Validating --> Rejected: Invalid input
    Validating --> Processing: Valid input

    Processing --> Preprocessing: Clean text
    Preprocessing --> Vectorizing: TF-IDF transform
    Vectorizing --> Predicting: Naive Bayes classify

    Predicting --> CheckingCache: Generate hash
    CheckingCache --> Found: Hash exists in DB
    CheckingCache --> Storing: Hash not found

    Found --> Returning: Return cached result
    Storing --> Persisting: Insert to database
    Persisting --> Returning: Return new result

    Returning --> Completed: Send response
    Rejected --> Completed: Send error

    Completed --> [*]

    note right of Processing
        ML Prediction happens here
        < 100ms typical
    end note

    note right of CheckingCache
        Deduplication optimization
        Avoids re-processing
    end note
```

---

## 8. Use Case Diagram - User Interactions

```mermaid
graph LR
    subgraph "Actors"
        User((User))
        Admin((Admin))
        System((System/Cron))
    end

    subgraph "Use Cases"
        UC1[Analyze Single Text]
        UC2[View Results]
        UC3[Check Dashboard Stats]
        UC4[Train New Model]
        UC5[Batch Analyze Texts]
        UC6[Export Data]
        UC7[Aggregate Analytics]
        UC8[Monitor System]
    end

    User --> UC1
    User --> UC2
    User --> UC3

    Admin --> UC4
    Admin --> UC5
    Admin --> UC6
    Admin --> UC8

    System --> UC7

    UC1 -.->|includes| UC2
    UC2 -.->|includes| UC3
    UC4 -.->|extends| UC1
    UC5 -.->|extends| UC1

    style UC1 fill:#4CAF50
    style UC4 fill:#FF9800
    style UC7 fill:#2196F3
```

---

## 9. Data Flow Diagram - End-to-End

```mermaid
flowchart TB
    Input[User Text Input] --> Validate{Input Valid?}

    Validate -->|No| Error[Return Error<br/>400 Bad Request]
    Validate -->|Yes| Hash[Generate SHA256<br/>text hash]

    Hash --> CheckDB{Hash exists<br/>in database?}

    CheckDB -->|Yes| Cached[Return cached<br/>analysis]
    CheckDB -->|No| Preprocess[Text Preprocessing<br/>Clean & normalize]

    Preprocess --> Vectorize[TF-IDF Vectorization<br/>Convert to features]
    Vectorize --> Classify[Naive Bayes<br/>Classification]

    Classify --> Scores[Calculate Scores<br/>pos/neu/neg]
    Scores --> Confidence[Determine Confidence<br/>max probability]

    Confidence --> SaveDB[(Save to<br/>Analysis table)]
    SaveDB --> Response[Build JSON Response]

    Response --> Return[Return to User]
    Cached --> Return
    Error --> Return

    Return --> UpdateStats[Trigger Stats Update]
    UpdateStats --> Aggregate[Aggregate Analytics]
    Aggregate --> StatsDB[(Save to<br/>AnalyticsSummary)]

    style Classify fill:#FF9800
    style SaveDB fill:#336791
    style Return fill:#4CAF50
```

---

## 10. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    ANALYSIS ||--o{ ANALYTICS_SUMMARY : aggregates
    TRAINING_DATA ||--o{ MODEL : trains
    MODEL ||--o{ ANALYSIS : "predicts with"

    ANALYSIS {
        int id PK
        varchar text_hash UK
        text text
        jsonb sentiment_scores
        jsonb emotion_scores
        enum predicted_label
        float confidence
        timestamp analyzed_at
        enum source
        jsonb extra_metadata
    }

    MODEL {
        int id PK
        varchar name
        varchar version
        varchar algorithm
        float f1_score
        int training_samples
        int vocabulary_size
        timestamp created_at
        boolean is_active
        varchar model_path
        jsonb metrics
    }

    TRAINING_DATA {
        int id PK
        text text
        enum label
        varchar source
        timestamp created_at
        boolean used_in_training
    }

    ANALYTICS_SUMMARY {
        int id PK
        timestamp date
        int hour
        float sentiment_avg
        int positive_count
        int neutral_count
        int negative_count
        int total_count
    }
```

---

## 11. Package Diagram - Code Organization

```mermaid
graph TB
    subgraph "sentiment-analysis"
        subgraph "apps/"
            API[api/<br/>FastAPI Backend]
            WEB[web/<br/>Next.js Frontend]
        end

        subgraph "packages/"
            ML[ml/<br/>ML Pipeline]
        end

        subgraph "observability/"
            PROM[prometheus/<br/>Metrics Config]
            GRAF[grafana/<br/>Dashboards]
        end

        CONFIG[docker-compose.yml<br/>Infrastructure]
        DOCS[Documentation<br/>MD files]
    end

    API --> ML
    WEB --> API

    API -.->|metrics| PROM
    PROM -.->|visualize| GRAF

    CONFIG --> API
    CONFIG --> WEB
    CONFIG --> PROM
    CONFIG --> GRAF

    style API fill:#4CAF50
    style WEB fill:#61DAFB
    style ML fill:#FF9800
```

---

## Rendering Instructions

### GitHub
These diagrams will render automatically when viewing this file on GitHub.

### VS Code
Install the "Markdown Preview Mermaid Support" extension.

### Online
Copy diagram code to [Mermaid Live Editor](https://mermaid.live).

### Export
Use Mermaid CLI or online tools to export as PNG/SVG:
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i UML_DIAGRAMS.md -o diagrams.pdf
```

---

## Legend

| Color | Meaning |
|-------|---------|
| 🟢 Green | Success/Active/Primary |
| 🔵 Blue | Processing/Analytics |
| 🟠 Orange | ML/AI Components |
| 🔴 Red | Errors/Warnings |
| ⚪ Gray | Neutral/Data |

| Symbol | Meaning |
|--------|---------|
| → | Data flow |
| -.-> | Metrics/Monitoring |
| -->> | Response |
| <--> | Bidirectional |

---

**Generated:** 2025-01-08
**Version:** 1.0.0
**Maintainer:** System Architecture Team
