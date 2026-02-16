# SAR Generation AI System

An advanced, AI-powered Suspicious Activity Report (SAR) generation system designed for banking compliance.

## Quick Start

### Prerequisites
- Python 3.10+
- Redis (for Celery)
- PostgreSQL (or change DB URL in .env)
- Ollama (running locally)

### Installation

1.  **Clone the repository**
    ```bash
    git clone <repo-url>
    cd barclays
    ```

2.  **Create Virtual Environment**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**
    Copy `.env.example` to `.env` (already created) and update values.

5.  **Run Application**
    ```bash
    uvicorn app.main:app --reload
    ```

6.  **Run Worker**
    ```bash
    celery -A app.core.celery_app worker --loglevel=info
    ```

## Architecture
- **API**: FastAPI
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL (Async)
- **AI**: Ollama + ChromaDB
