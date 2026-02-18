# SAR Generation AI System

An AI-powered Suspicious Activity Report (SAR) generation system designed for banking compliance, leveraging LLMs to automate narrative drafting.

## 🚀 Key Features

*   **Dynamic Case Discovery**:
    *   Automatically detects potential cases from transaction data.
    *   **Smart Risk Rating**: Dynamically calculates HIGH/MEDIUM/LOW risk based on alerts and transaction anomalies.
    *   **Anomaly Detection**: Backend statistical analysis flags "spikes" and high-value transactions.
*   **AI-Powered Generation**:
    *   Generates comprehensive SAR narratives using local LLMs (Ollama/Llama 3).
    *   Context-aware templates for different regions (e.g., India vs US).
*   **Interactive Compliance Dashboard**:
    *   Visual "Case Discovery" tab with risk badges.
    *   **Submitted Reports History**: View and audit all generated reports.
    *   **Review & Edit**: Compliance officers can review and edit drafts before final submission.

## 🛠 Tech Stack

*   **Backend**: Python (FastAPI), SQLAlchemy (Async), Pydantic
*   **Database**: SQLite (Async) for easy setup
*   **Task Queue**: Celery + Redis
*   **AI Engine**: Ollama (Local Llama 3)
*   **Frontend**: Vanilla JS + HTML5 (Lightweight)

## 📋 Prerequisites

1.  **Python 3.10+**
2.  **Redis Server** (Must be running locally on default port 6379)
3.  **Ollama** (Must be installed and running with `llama3` model pulled)
    *   `ollama pull llama3`

## ⚡ Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repo-url>
cd barclays

# Create Virtual Environment
python -m venv venv
.\venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

### 2. Configuration

Ensure `.env` exists with the following (default provided):

```ini
DATABASE_URL=sqlite+aiosqlite:///./sql_app.db
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Seed Database (Important!)

Populate the database with test cases (High/Medium/Low risk scenarios):

```bash
python scripts/seed_db.py
```

### 4. Run Application

You can start all services individually:

**Terminal 1: Backend API**
```bash
uvicorn app.main:app --reload --port 8000
```

**Terminal 2: Celery Worker**
```bash
celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

**Terminal 3: Frontend**
```bash
cd frontend
python -m http.server 3000
```

### 5. Usage

1.  Open your browser to `http://localhost:3000`.
2.  **Case Discovery**: Browse the list of detected cases. Note the Risk Ratings.
3.  **Inspect**: Click "Inspect Case" to view customer details and transactions.
    *   *Red Highlights*: Indicate anomalies/spikes.
4.  **Generate**: Select transactions and click "Generate SAR Report".
5.  **Review**: Edit the generated draft and click "Submit".
6.  **History**: Check the "Submitted Reports" tab to view archived SARs.
