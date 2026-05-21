from typing import Optional
from fastapi import APIRouter, Query
from app.database import run_query
from app.pagination import apply_pagination
from app.cache import cache_get_set
from app.validators import (
    validate, validate_year,
    VALID_MARKET_TYPES, VALID_CROP_CATEGORIES, VALID_SEASONS, VALID_PRICE_TIERS,
)

router = APIRouter(prefix="/markets", tags=["Market Intelligence"])


@router.get("/price-comparison")
async def price_comparison(
    market_type: Optional[str] = Query(None, description="Local | Wholesale | Export | Retail | Government Procurement", example="Export"),
    crop_category: Optional[str] = Query(None, description="Cereal | Vegetable | Fruit | Pulse | Oilseed | Cash Crop | Spice", example="Cereal"),
    year: Optional[int] = Query(None, description="2022 | 2023 | 2024", example=2023, ge=2022, le=2024),
    season: Optional[str] = Query(None, description="Spring | Summer | Autumn | Winter", example="Spring"),
    price_tier: Optional[str] = Query(None, description="Low | Medium | High | Premium", example="High"),
    district: Optional[str] = Query(None, description="Filter by district name", example="Gazipur"),
    limit: int = Query(50, description="Number of results per page", example=50, ge=1, le=100),
    offset: int = Query(0, description="Number of results to skip", example=0, ge=0),
):
    filters_applied = {k: v for k, v in {"market_type": market_type, "crop_category": crop_category, "year": year, "season": season, "price_tier": price_tier, "district": district}.items() if v is not None}
    market_type = validate(market_type, VALID_MARKET_TYPES, "market_type") or market_type
    crop_category = validate(crop_category, VALID_CROP_CATEGORIES, "crop_category") or crop_category
    validate_year(year)
    season = validate(season, VALID_SEASONS, "season") or season
    price_tier = validate(price_tier, VALID_PRICE_TIERS, "price_tier") or price_tier
    cache_key = "price_comparison:" + ":".join(f"{k}={v}" for k, v in filters_applied.items())

    async def fetch():
        df = await run_query("SELECT * FROM vw_harvest_full")
        if market_type:
            df = df[df["market_type"] == market_type]
        if crop_category:
            df = df[df["crop_category"] == crop_category]
        if year:
            df = df[df["year"] == year]
        if season:
            df = df[df["season"] == season]
        if price_tier:
            df = df[df["price_tier"] == price_tier]
        if district:
            df = df[df["farm_district"].str.lower() == district.lower()]
        if df.empty:
            return []
        comparison = (
            df.groupby(["market_name", "market_type", "price_tier", "farm_district", "crop_name"], as_index=False)
            .agg(avg_price_per_ton_bdt=("price_per_ton_bdt", "mean"), total_quantity_sold_ton=("quantity_sold_ton", "sum"), total_revenue_bdt=("revenue_bdt", "sum"))
        )
        comparison = comparison.rename(columns={"farm_district": "district"})
        comparison["avg_price_per_ton_bdt"] = comparison["avg_price_per_ton_bdt"].round(2)
        comparison["total_quantity_sold_ton"] = comparison["total_quantity_sold_ton"].round(2)
        comparison["total_revenue_bdt"] = comparison["total_revenue_bdt"].round(2)
        comparison = comparison.sort_values("avg_price_per_ton_bdt", ascending=False)
        return comparison.to_dict(orient="records")

    results = await cache_get_set(cache_key, fetch, expire=120)
    paged = apply_pagination(results, limit, offset)
    return {"filters_applied": filters_applied, "limit": limit, "offset": offset, "comparison": paged}
