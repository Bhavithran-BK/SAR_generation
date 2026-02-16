from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

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
if settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.ALLOWED_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
