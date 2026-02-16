from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # DATABASE
    DATABASE_URL: str
    
    # REDIS / CELERY
    REDIS_HOST: str
    REDIS_PORT: int
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # OLLAMA
    OLLAMA_BASE_URL: str
    
    # CORS
    ALLOWED_ORIGINS: List[AnyHttpUrl] = []

    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[AnyHttpUrl]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
