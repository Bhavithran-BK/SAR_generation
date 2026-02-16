from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import generation, batch
# Ensure configs are loaded
import app.core.configs.india 

# Placeholder for future initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup:
    print("Starting up SAR Generation System...")
    # Initialize DB connection (TODO)
    # Initialize ML models (TODO)
    yield
    # Shutdown:
    print("Shutting down SAR Generation System...")
    # Close DB connection (TODO)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generation.router, prefix="/api/v1/generation", tags=["Generation"])
app.include_router(batch.router, prefix="/api/v1/batch", tags=["Batch Processing"])

@app.get("/health")
async def health_check():
    try:
        # Check DB connection using a simple query
        from app.db.base import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"failed: {str(e)}"
    
    return {
        "status": "ok", 
        "project": settings.PROJECT_NAME,
        "database": db_status
    }

@app.get("/")
def root():
    return {"message": "Welcome to SAR Generation AI System API"}
