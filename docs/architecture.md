# SAR Generation System - Architecture & Workflow

## 1. Workflow Diagram (Mermaid)

```mermaid
sequenceDiagram
    participant U as Compliance User
    participant FE as Frontend (JS/HTML)
    participant API as Backend API (FastAPI)
    participant DB as Database (SQLite)
    participant Q as Redis Queue
    participant W as Celery Worker
    participant AI as LLM Engine (Ollama)

    Note over U, FE: Case Discovery Phase
    U->>FE: Open Dashboard (Case Discovery)
    FE->>API: GET /cases (Fetch Active Cases)
    API->>DB: Query Transactions & Alerts
    DB-->>API: Return Aggregated Case Data
    API-->>FE: Return Cases with Risk Ratings
    FE-->>U: Display Cases (High/Med/Low Badges)

    Note over U, FE: Investigation Phase
    U->>FE: Select Case & Transactions
    FE->>U: Highlight Anomalies (Red)
    U->>FE: Click "Generate SAR Report"
    FE->>API: POST /generation/generate (Selected Tx IDs)
    
    Note over API, W: Async Processing Phase
    API->>Q: Push Job (Case ID, Tx IDs)
    API-->>FE: Return Job ID (Status: PENDING)
    FE->>API: Poll Status (Interval)
    Q->>W: Fetch Job
    W->>DB: Fetch Full Case Context
    W->>W: Run Rule-Based Analysis (Structuring/Spikes)
    W->>AI: Send Prompt + Context (JSON)
    AI-->>W: Return Narrative Draft
    W->>DB: Save Draft (Status: GENERATED)
    W-->>Q: Update Job Status (COMPLETED)

    Note over U, FE: Review & Submission Phase
    API-->>FE: Return Status: COMPLETED + Draft Content
    FE->>U: Display Review Modal
    U->>FE: Edit Narrative & Click Submit
    FE->>API: POST /generation/save (Edited Content)
    FE->>API: POST /generation/finalize
    API->>DB: Update Status: SUBMITTED & Audit Log
    API-->>FE: Success
    FE-->>U: Show Success Message
```

## 2. Architecture Diagram Prompt

You can use the following prompt with any AI image generator (like ChatGPT/DALL-E 3, Midjourney) or diagramming tool to visualize the entire system architecture.

**Copy and Paste this Prompt:**

> **Subject:** Technical Architecture Diagram for an AI-Powered SAR (Suspicious Activity Report) Generation System.
> 
> **Style:** High-level system architecture diagram, clean, modern, professional, cloud-native aesthetic. Use distinct icons for different technologies.
> 
> **Components to Include:**
> 1.  **Frontend Layer (User Interface):**
>     *   **"Compliance Dashboard"**: A web interface (HTML/JS) showing "Case Discovery" and "Report Editor".
>     *   **Action Arrow**: User selects transactions -> Sends request to Backend.
> 
> 2.  **API Layer (Backend):**
>     *   **"FastAPI Server"**: The central orchestrator handling REST API requests.
>     *   **Features/Modules inside API**: 
>         *   "Risk Engine" (Calculates High/Med/Low risk).
>         *   "Anomaly Detector" (Statistical spike detection).
>         *   "Auth & Rate Limiting".
> 
> 3.  **Data Layer (Persistence):**
>     *   **"SQLite / PostgreSQL Database"**: Stores "Transactions", "Alerts", "Customer Profiles", and "SAR History".
>     *   **"Seed Data"**: Show an input arrow representing "Mock High-Risk/Low-Risk Scenarios".
> 
> 4.  **Async Processing Layer (The "Brain"):**
>     *   **"Redis Queue"**: Buffers generation requests from the API.
>     *   **"Celery Worker"**: Consumes tasks from Redis. Performs deep analysis.
>     *   **"Analysis Engine"**: A component inside the worker that runs rule-based logic (e.g., "Structuring Check").
> 
> 5.  **AI Engine (The Generator):**
>     *   **"Ollama (Local LLM)"**: Represents the AI model (Llama 3).
>     *   **Flow**: Celery Worker sends "Prompt + Context" -> Ollama returns "Narrative Draft".
> 
> **Data Flow Arrows:**
> *   **User** -> **Frontend** -> **FastAPI**
> *   **FastAPI** <-> **Database** (Reads Cases / Saves Reports)
> *   **FastAPI** -> **Redis** -> **Celery Worker**
> *   **Celery Worker** <-> **Ollama** (Generation Loop)
> *   **Celery Worker** -> **Database** (Saves Generated Draft)
> 
> **Key Labels/Annotations:**
> *   "Dynamic Risk Scoring" (near API/Database)
> *   "Context-Aware Generation" (near Ollama)
> *   "Audit Trail" (near Database/History)
> *   "Local Execution" (emphasize data privacy)
