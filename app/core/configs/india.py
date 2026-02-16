from app.core.region_config import RegionConfig, RegionFactory

india_config = RegionConfig(
    currency_symbol="₹",
    currency_code="INR",
    date_format="%d-%m-%Y",
    regulator_name="FIU-IND",
    report_name="Suspicious Transaction Report (STR)",
    thresholds={
        "structuring": 1000000.0, # 10 Lakhs
        "rapid_movement": 500000.0 # 5 Lakhs
    }
)

# Register automatically when imported
RegionFactory.register("IND", india_config) 
RegionFactory.register("IN", india_config)
