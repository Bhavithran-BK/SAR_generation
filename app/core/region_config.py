from typing import Dict, Any
from pydantic import BaseModel

class RegionConfig(BaseModel):
    currency_symbol: str
    currency_code: str
    date_format: str
    regulator_name: str
    report_name: str
    thresholds: Dict[str, float]
    
    # Formatting functions (optional, but Pydantic keeps data)
    
class RegionFactory:
    _configs = {}
    
    @classmethod
    def register(cls, region_code: str, config: RegionConfig):
        cls._configs[region_code.upper()] = config
        
    @classmethod
    def get(cls, region_code: str) -> RegionConfig:
        return cls._configs.get(region_code.upper(), cls._configs.get("US")) # Default to US

# Base US Config (Default)
us_config = RegionConfig(
    currency_symbol="$",
    currency_code="USD",
    date_format="%Y-%m-%d",
    regulator_name="FinCEN",
    report_name="Suspicious Activity Report",
    thresholds={
        "structuring": 10000.0,
        "rapid_movement": 5000.0
    }
)

RegionFactory.register("US", us_config)

# Import other regions to ensure registration
from app.core.configs import india
