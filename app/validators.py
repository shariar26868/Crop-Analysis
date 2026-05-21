from fastapi import HTTPException

VALID_REGIONS = {"Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna", "Rangpur", "Barisal", "Mymensingh"}
VALID_FARM_TYPES = {"Small", "Medium", "Large", "Commercial"}
VALID_CROP_CATEGORIES = {"Cereal", "Vegetable", "Fruit", "Pulse", "Oilseed", "Cash Crop", "Spice"}
VALID_SEASONS = {"Spring", "Summer", "Autumn", "Winter"}
VALID_GROWING_SEASONS = {"Rabi", "Kharif", "Zaid", "Year-Round"}
VALID_MARKET_TYPES = {"Local", "Wholesale", "Export", "Retail", "Government Procurement"}
VALID_PRICE_TIERS = {"Low", "Medium", "High", "Premium"}
VALID_QUALITY_GRADES = {"A", "B", "C", "D"}
VALID_PESTICIDE_RESIDUES = {"None", "Trace", "Low", "High"}
VALID_WATER_REQUIREMENTS = {"Low", "Medium", "High"}
VALID_YEARS = {2022, 2023, 2024}
VALID_QUARTERS = {1, 2, 3, 4}
VALID_METRICS = {"profit", "revenue", "yield"}

def validate(value, valid_set: set, param_name: str):
    if value is not None:
        stripped = value.strip()
        matched = next((v for v in valid_set if v.lower() == stripped.lower()), None)
        if matched is None:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid value '{stripped}' for '{param_name}'. Accepted: {sorted(valid_set)}"
            )
        return matched  
    return value

def validate_year(year):
    if year is not None and year not in VALID_YEARS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid year '{year}'. Accepted: 2022, 2023, 2024"
        )

def validate_quarter(quarter):
    if quarter is not None and quarter not in VALID_QUARTERS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid quarter '{quarter}'. Accepted: 1, 2, 3, 4"
        )