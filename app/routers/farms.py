from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.database import run_query
from app.pagination import apply_pagination
from app.cache import cache_get_set
from app.validators import (
    validate, validate_year,
    VALID_REGIONS, VALID_FARM_TYPES, VALID_SEASONS,
    VALID_CROP_CATEGORIES, VALID_MARKET_TYPES, VALID_QUALITY_GRADES, VALID_METRICS,
)

router = APIRouter(prefix="/farms", tags=["Farm Performance"])


@router.get("/summary")
async def farm_summary(
    region: Optional[str] = Query(None, description="Dhaka | Chittagong | Sylhet | Rajshahi | Khulna | Rangpur | Barisal | Mymensingh", example="Rajshahi"),
    farm_type: Optional[str] = Query(None, description="Small | Medium | Large | Commercial", example="Medium"),
    year: Optional[int] = Query(None, description="2022 | 2023 | 2024", example=2023, ge=2022, le=2024),
    season: Optional[str] = Query(None, description="Spring | Summer | Autumn | Winter", example="Summer"),
    limit: int = Query(50, description="Number of results per page", example=50, ge=1, le=100),
    offset: int = Query(0, description="Number of results to skip", example=0, ge=0),
):
    region = validate(region, VALID_REGIONS, "region") or region
    farm_type = validate(farm_type, VALID_FARM_TYPES, "farm_type") or farm_type
    season = validate(season, VALID_SEASONS, "season") or season
    validate_year(year)
    filters_applied = {k: v for k, v in {"region": region, "farm_type": farm_type, "year": year, "season": season}.items() if v is not None}
    cache_key = "farms:summary:" + ":".join(f"{k}={v}" for k, v in filters_applied.items()) + f":limit={limit}:offset={offset}"

    async def fetch():
        df = await run_query("SELECT * FROM vw_harvest_full")
        if region:
            df = df[df["region"] == region]
        if farm_type:
            df = df[df["farm_type"] == farm_type]
        if year:
            df = df[df["year"] == year]
        if season:
            df = df[df["season"] == season]
        if df.empty:
            return {"total_farms": 0, "data": []}
        summary = (
            df.groupby(["farm_name", "region", "farm_type"], as_index=False)
            .agg(
                total_revenue_bdt=("revenue_bdt", "sum"),
                total_cost_bdt=("input_cost_bdt", "sum"),
                net_profit_bdt=("net_profit_bdt", "sum"),
                avg_loss_pct=("quantity_lost_ton", lambda x: round(
                    (x.sum() / df.loc[x.index, "quantity_harvested_ton"].sum()) * 100, 2
                )),
            )
        )
        summary["total_revenue_bdt"] = summary["total_revenue_bdt"].round(2)
        summary["total_cost_bdt"] = summary["total_cost_bdt"].round(2)
        summary["net_profit_bdt"] = summary["net_profit_bdt"].round(2)
        return {"total_farms": len(summary), "data": summary.to_dict(orient="records")}

    result = await cache_get_set(cache_key, fetch, expire=120)
    total = result.get("total_farms", 0)
    records = result.get("data", [])
    paged = apply_pagination(records, limit, offset)
    return {"total_farms": total, "filters_applied": filters_applied, "limit": limit, "offset": offset, "data": paged}


@router.get("/{farm_id}/performance")
async def farm_performance(
    farm_id: int,
    year: Optional[int] = Query(None, description="2022 | 2023 | 2024", example=2023, ge=2022, le=2024),
    crop_category: Optional[str] = Query(None, description="Cereal | Vegetable | Fruit | Pulse | Oilseed | Cash Crop | Spice", example="Cereal"),
    market_type: Optional[str] = Query(None, description="Local | Wholesale | Export | Retail | Government Procurement", example="Wholesale"),
):
    df = await run_query("SELECT * FROM vw_harvest_full")
    farms_df = await run_query("SELECT * FROM dim_farm")
    validate_year(year)
    crop_category = validate(crop_category, VALID_CROP_CATEGORIES, "crop_category") or crop_category
    market_type = validate(market_type, VALID_MARKET_TYPES, "market_type") or market_type
    farm_row = farms_df[farms_df["farm_id"] == farm_id]
    if farm_row.empty:
        raise HTTPException(status_code=404, detail=f"Farm with id={farm_id} not found.")
    farm_name = farm_row.iloc[0]["farm_name"]
    owner = farm_row.iloc[0]["owner_name"]
    region = farm_row.iloc[0]["region"]
    farm_df = df[df["farm_name"] == farm_name].copy()
    if year:
        farm_df = farm_df[farm_df["year"] == year]
    if crop_category:
        farm_df = farm_df[farm_df["crop_category"] == crop_category]
    if market_type:
        farm_df = farm_df[farm_df["market_type"] == market_type]
    performance = (
        farm_df.groupby(["crop_name", "year", "market_type", "quality_grade"], as_index=False)
        .agg(
            quantity_sold_ton=("quantity_sold_ton", "sum"),
            revenue_bdt=("revenue_bdt", "sum"),
            net_profit_bdt=("net_profit_bdt", "sum"),
        )
    )
    performance["quantity_sold_ton"] = performance["quantity_sold_ton"].round(2)
    performance["revenue_bdt"] = performance["revenue_bdt"].round(2)
    performance["net_profit_bdt"] = performance["net_profit_bdt"].round(2)
    filters_applied = {k: v for k, v in {"year": year, "crop_category": crop_category, "market_type": market_type}.items() if v is not None}
    return {"farm_id": farm_id, "farm_name": farm_name, "owner": owner, "region": region, "filters_applied": filters_applied, "performance": performance.to_dict(orient="records")}


@router.get("/top")
async def top_farms(
    metric: str = Query("profit", description="profit | revenue | yield", example="profit"),
    region: Optional[str] = Query(None, description="Dhaka | Chittagong | Sylhet | Rajshahi | Khulna | Rangpur | Barisal | Mymensingh", example="Dhaka"),
    farm_type: Optional[str] = Query(None, description="Small | Medium | Large | Commercial", example="Large"),
    year: Optional[int] = Query(None, description="2022 | 2023 | 2024", example=2024, ge=2022, le=2024),
    limit: int = Query(10, description="Number of top farms to return", example=10, gt=0),
):
    metric = validate(metric, VALID_METRICS, "metric") or metric
    region = validate(region, VALID_REGIONS, "region") or region
    farm_type = validate(farm_type, VALID_FARM_TYPES, "farm_type") or farm_type
    validate_year(year)
    filters_applied = {k: v for k, v in {"metric": metric, "region": region, "farm_type": farm_type, "year": year, "limit": limit}.items() if v is not None}
    cache_key = "farms:top:" + ":".join(f"{k}={v}" for k, v in filters_applied.items())

    async def fetch_top():
        df = await run_query("SELECT * FROM vw_harvest_full")
        if region:
            df = df[df["region"] == region]
        if farm_type:
            df = df[df["farm_type"] == farm_type]
        if year:
            df = df[df["year"] == year]
        if df.empty:
            return []
        grouped = (
            df.groupby(["farm_name", "region", "farm_type"], as_index=False)
            .agg(
                total_revenue_bdt=("revenue_bdt", "sum"),
                net_profit_bdt=("net_profit_bdt", "sum"),
                total_area_ha=("area_planted_ha", "sum"),
                total_harvested_ton=("quantity_harvested_ton", "sum"),
            )
        )
        grouped["yield_efficiency"] = (grouped["total_harvested_ton"] / grouped["total_area_ha"]).round(3)
        sort_col = {"profit": "net_profit_bdt", "revenue": "total_revenue_bdt", "yield": "yield_efficiency"}.get(metric, "net_profit_bdt")
        ranked = grouped.sort_values(sort_col, ascending=False).head(limit).reset_index(drop=True)
        ranked["rank"] = ranked.index + 1
        ranked["total_revenue_bdt"] = ranked["total_revenue_bdt"].round(2)
        ranked["net_profit_bdt"] = ranked["net_profit_bdt"].round(2)
        return ranked[["rank", "farm_name", "region", "farm_type", "net_profit_bdt", "total_revenue_bdt", "yield_efficiency"]].to_dict(orient="records")

    ranked_list = await cache_get_set(cache_key, fetch_top, expire=120)
    return {"metric": metric, "filters_applied": filters_applied, "rankings": ranked_list}


@router.get("/loss-analysis")
async def loss_analysis(
    region: Optional[str] = Query(None, description="Dhaka | Chittagong | Sylhet | Rajshahi | Khulna | Rangpur | Barisal | Mymensingh", example="Khulna"),
    year: Optional[int] = Query(None, description="2022 | 2023 | 2024", example=2023, ge=2022, le=2024),
    season: Optional[str] = Query(None, description="Spring | Summer | Autumn | Winter", example="Winter"),
    quality_grade: Optional[str] = Query(None, description="A | B | C | D", example="A"),
    crop_category: Optional[str] = Query(None, description="Cereal | Vegetable | Fruit | Pulse | Oilseed | Cash Crop | Spice", example="Vegetable"),
):
    df = await run_query("SELECT * FROM vw_harvest_full")
    region = validate(region, VALID_REGIONS, "region") or region
    validate_year(year)
    season = validate(season, VALID_SEASONS, "season") or season
    quality_grade = validate(quality_grade, VALID_QUALITY_GRADES, "quality_grade") or quality_grade
    crop_category = validate(crop_category, VALID_CROP_CATEGORIES, "crop_category") or crop_category
    if region:
        df = df[df["region"] == region]
    if year:
        df = df[df["year"] == year]
    if season:
        df = df[df["season"] == season]
    if quality_grade:
        df = df[df["quality_grade"] == quality_grade]
    if crop_category:
        df = df[df["crop_category"] == crop_category]
    filters_applied = {k: v for k, v in {"region": region, "year": year, "season": season, "quality_grade": quality_grade, "crop_category": crop_category}.items() if v is not None}
    if df.empty:
        return {"filters_applied": filters_applied, "summary": {"total_harvested_ton": 0, "total_lost_ton": 0, "overall_loss_pct": 0}, "breakdown": []}
    total_harvested = df["quantity_harvested_ton"].sum()
    total_lost = df["quantity_lost_ton"].sum()
    overall_loss_pct = round((total_lost / total_harvested) * 100, 2) if total_harvested > 0 else 0
    breakdown = (
        df.groupby(["region", "crop_category", "quality_grade", "pesticide_residue"], as_index=False)
        .agg(total_harvested_ton=("quantity_harvested_ton", "sum"), total_lost_ton=("quantity_lost_ton", "sum"))
    )
    breakdown["loss_pct"] = (breakdown["total_lost_ton"] / breakdown["total_harvested_ton"] * 100).round(2)
    breakdown["total_lost_ton"] = breakdown["total_lost_ton"].round(3)
    breakdown["total_harvested_ton"] = breakdown["total_harvested_ton"].round(3)
    breakdown = breakdown.sort_values("loss_pct", ascending=False)
    return {"filters_applied": filters_applied, "summary": {"total_harvested_ton": round(float(total_harvested), 3), "total_lost_ton": round(float(total_lost), 3), "overall_loss_pct": overall_loss_pct}, "breakdown": breakdown.to_dict(orient="records")}
