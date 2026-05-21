from typing import Optional
from fastapi import Query
from pydantic import BaseModel, conint

class QueryModelBase(BaseModel):
    class Config:
        str_strip_whitespace = True
        from_attributes = True

class FarmSummaryQuery(QueryModelBase):
    region: Optional[str] = Query(
        None,
        description="Filter by region",
        example="Rajshahi",
        openapi_extra={"x-enum-values": "Dhaka | Chittagong | Sylhet | Rajshahi | Khulna | Rangpur | Barisal | Mymensingh"},
    )
    farm_type: Optional[str] = Query(
        None,
        description="Filter by farm type: Small | Medium | Large | Commercial",
        example="Medium",
    )
    year: Optional[int] = Query(
        None,
        description="Filter by year: 2022 | 2023 | 2024",
        example=2023,
        ge=2022,
        le=2024,
    )
    season: Optional[str] = Query(
        None,
        description="Filter by season: Spring | Summer | Autumn | Winter",
        example="Summer",
    )

class FarmPerformanceQuery(QueryModelBase):
    year: Optional[int] = Query(
        None,
        description="Filter by year: 2022 | 2023 | 2024",
        example=2023,
        ge=2022,
        le=2024,
    )
    crop_category: Optional[str] = Query(
        None,
        description="Filter by crop category: Cereal | Vegetable | Fruit | Pulse | Oilseed | Cash Crop | Spice",
        example="Cereal",
    )
    market_type: Optional[str] = Query(
        None,
        description="Filter by market type: Local | Wholesale | Export | Retail | Government Procurement",
        example="Wholesale",
    )

class TopFarmsQuery(QueryModelBase):
    metric: str = Query(
        "profit",
        description="Sort metric: profit | revenue | yield",
        example="profit",
    )
    region: Optional[str] = Query(
        None,
        description="Filter by region: Dhaka | Chittagong | Sylhet | Rajshahi | Khulna | Rangpur | Barisal | Mymensingh",
        example="Dhaka",
    )
    farm_type: Optional[str] = Query(
        None,
        description="Filter by farm type: Small | Medium | Large | Commercial",
        example="Large",
    )
    year: Optional[int] = Query(
        None,
        description="Filter by year: 2022 | 2023 | 2024",
        example=2024,
        ge=2022,
        le=2024,
    )
    limit: int = Query(
        10,
        description="Number of top farms to return",
        example=10,
        gt=0,
    )

class LossAnalysisQuery(QueryModelBase):
    region: Optional[str] = Query(
        None,
        description="Filter by region: Dhaka | Chittagong | Sylhet | Rajshahi | Khulna | Rangpur | Barisal | Mymensingh",
        example="Khulna",
    )
    year: Optional[int] = Query(
        None,
        description="Filter by year: 2022 | 2023 | 2024",
        example=2023,
        ge=2022,
        le=2024,
    )
    season: Optional[str] = Query(
        None,
        description="Filter by season: Spring | Summer | Autumn | Winter",
        example="Winter",
    )
    quality_grade: Optional[str] = Query(
        None,
        description="Filter by quality grade: A | B | C | D",
        example="A",
    )
    crop_category: Optional[str] = Query(
        None,
        description="Filter by crop category: Cereal | Vegetable | Fruit | Pulse | Oilseed | Cash Crop | Spice",
        example="Vegetable",
    )

class CropYieldEfficiencyQuery(QueryModelBase):
    crop_category: Optional[str] = Query(
        None,
        description="Filter by crop category: Cereal | Vegetable | Fruit | Pulse | Oilseed | Cash Crop | Spice",
        example="Cereal",
    )
    season: Optional[str] = Query(
        None,
        description="Filter by season: Spring | Summer | Autumn | Winter",
        example="Autumn",
    )
    year: Optional[int] = Query(
        None,
        description="Filter by year: 2022 | 2023 | 2024",
        example=2022,
        ge=2022,
        le=2024,
    )
    region: Optional[str] = Query(
        None,
        description="Filter by region: Dhaka | Chittagong | Sylhet | Rajshahi | Khulna | Rangpur | Barisal | Mymensingh",
        example="Sylhet",
    )
    water_requirement: Optional[str] = Query(
        None,
        description="Filter by water requirement: Low | Medium | High",
        example="Medium",
    )

class SeasonalTrendQuery(QueryModelBase):
    crop_name: Optional[str] = Query(
        None,
        description="Filter by crop name",
        example="Boro Rice",
    )
    crop_category: Optional[str] = Query(
        None,
        description="Filter by crop category: Cereal | Vegetable | Fruit | Pulse | Oilseed | Cash Crop | Spice",
        example="Cereal",
    )
    year: Optional[int] = Query(
        None,
        description="Filter by year: 2022 | 2023 | 2024",
        example=2023,
        ge=2022,
        le=2024,
    )
    quarter: Optional[int] = Query(
        None,
        description="Filter by quarter: 1 | 2 | 3 | 4",
        example=2,
        ge=1,
        le=4,
    )
    market_type: Optional[str] = Query(
        None,
        description="Filter by market type: Local | Wholesale | Export | Retail | Government Procurement",
        example="Export",
    )

class QualityBreakdownQuery(QueryModelBase):
    crop_id: Optional[int] = Query(
        None,
        description="Filter by crop ID from dim_crop table",
        example=5,
    )
    crop_category: Optional[str] = Query(
        None,
        description="Filter by crop category: Cereal | Vegetable | Fruit | Pulse | Oilseed | Cash Crop | Spice",
        example="Fruit",
    )
    year: Optional[int] = Query(
        None,
        description="Filter by year: 2022 | 2023 | 2024",
        example=2024,
        ge=2022,
        le=2024,
    )
    region: Optional[str] = Query(
        None,
        description="Filter by region: Dhaka | Chittagong | Sylhet | Rajshahi | Khulna | Rangpur | Barisal | Mymensingh",
        example="Chittagong",
    )
    market_type: Optional[str] = Query(
        None,
        description="Filter by market type: Local | Wholesale | Export | Retail | Government Procurement",
        example="Retail",
    )
    pesticide_residue: Optional[str] = Query(
        None,
        description="Filter by pesticide residue: None | Trace | Low | High",
        example="Trace",
    )

class MarketComparisonQuery(QueryModelBase):
    market_type: Optional[str] = Query(
        None,
        description="Filter by market type: Local | Wholesale | Export | Retail | Government Procurement",
        example="Export",
    )
    crop_category: Optional[str] = Query(
        None,
        description="Filter by crop category: Cereal | Vegetable | Fruit | Pulse | Oilseed | Cash Crop | Spice",
        example="Cereal",
    )
    year: Optional[int] = Query(
        None,
        description="Filter by year: 2022 | 2023 | 2024",
        example=2023,
        ge=2022,
        le=2024,
    )
    season: Optional[str] = Query(
        None,
        description="Filter by season: Spring | Summer | Autumn | Winter",
        example="Spring",
    )
    price_tier: Optional[str] = Query(
        None,
        description="Filter by price tier: Low | Medium | High | Premium",
        example="High",
    )
    district: Optional[str] = Query(
        None,
        description="Filter by district name",
        example="Gazipur",
    )
