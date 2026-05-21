from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.database import run_query
from app.cache import cache_get_set
from app.validators import (
    validate, validate_year, validate_quarter,
    VALID_REGIONS, VALID_SEASONS, VALID_CROP_CATEGORIES,
    VALID_MARKET_TYPES, VALID_PESTICIDE_RESIDUES, VALID_WATER_REQUIREMENTS,
)

router = APIRouter(prefix="/crops", tags=["Crop & Market Intelligence"])


@router.get("/yield-efficiency")
async def yield_efficiency(
    crop_category: Optional[str] = Query(None, description="Cereal | Vegetable | Fruit | Pulse | Oilseed | Cash Crop | Spice", example="Cereal"),
    season: Optional[str] = Query(None, description="Spring | Summer | Autumn | Winter", example="Autumn"),
    year: Optional[int] = Query(None, description="2022 | 2023 | 2024", example=2022, ge=2022, le=2024),
    region: Optional[str] = Query(None, description="Dhaka | Chittagong | Sylhet | Rajshahi | Khulna | Rangpur | Barisal | Mymensingh", example="Sylhet"),
    water_requirement: Optional[str] = Query(None, description="Low | Medium | High", example="Medium"),
):
    crop_category = validate(crop_category, VALID_CROP_CATEGORIES, "crop_category") or crop_category
    season = validate(season, VALID_SEASONS, "season") or season
    validate_year(year)
    region = validate(region, VALID_REGIONS, "region") or region
    water_requirement = validate(water_requirement, VALID_WATER_REQUIREMENTS, "water_requirement") or water_requirement
    filters_applied = {k: v for k, v in {"crop_category": crop_category, "season": season, "year": year, "region": region, "water_requirement": water_requirement}.items() if v is not None}
    cache_key = "crops:yield_efficiency:" + ":".join(f"{k}={v}" for k, v in filters_applied.items())

    async def fetch():
        harvest_df = await run_query("SELECT * FROM vw_harvest_full")
        crop_df = await run_query("SELECT * FROM dim_crop")
        if crop_category:
            harvest_df = harvest_df[harvest_df["crop_category"] == crop_category]
        if season:
            harvest_df = harvest_df[harvest_df["season"] == season]
        if year:
            harvest_df = harvest_df[harvest_df["year"] == year]
        if region:
            harvest_df = harvest_df[harvest_df["region"] == region]
        if harvest_df.empty:
            return []
        merged = harvest_df.merge(
            crop_df[["crop_name", "avg_yield_ton_per_ha", "water_requirement"]],
            on="crop_name", how="left",
        )
        if water_requirement:
            merged = merged[merged["water_requirement"] == water_requirement]
        merged["actual_yield"] = merged["quantity_harvested_ton"] / merged["area_planted_ha"]
        grouped = (
            merged.groupby(["crop_name", "crop_category", "growing_season", "avg_yield_ton_per_ha"], as_index=False)
            .agg(actual_avg_yield_ton_per_ha=("actual_yield", "mean"), total_area_planted_ha=("area_planted_ha", "sum"))
        )
        grouped["efficiency_pct"] = (grouped["actual_avg_yield_ton_per_ha"] / grouped["avg_yield_ton_per_ha"] * 100).round(2)
        grouped["actual_avg_yield_ton_per_ha"] = grouped["actual_avg_yield_ton_per_ha"].round(3)
        grouped["total_area_planted_ha"] = grouped["total_area_planted_ha"].round(2)
        grouped = grouped.rename(columns={"avg_yield_ton_per_ha": "avg_yield_benchmark_ton_per_ha", "growing_season": "season"})
        grouped = grouped.sort_values("efficiency_pct", ascending=False)
        return grouped.to_dict(orient="records")

    result = await cache_get_set(cache_key, fetch, expire=120)
    return {"filters_applied": filters_applied, "data": result}


@router.get("/seasonal-trend")
async def seasonal_trend(
    crop_name: Optional[str] = Query(None, description="Filter by crop name", example="Boro Rice"),
    crop_category: Optional[str] = Query(None, description="Cereal | Vegetable | Fruit | Pulse | Oilseed | Cash Crop | Spice", example="Cereal"),
    year: Optional[int] = Query(None, description="2022 | 2023 | 2024", example=2023, ge=2022, le=2024),
    quarter: Optional[int] = Query(None, description="1 | 2 | 3 | 4", example=2, ge=1, le=4),
    market_type: Optional[str] = Query(None, description="Local | Wholesale | Export | Retail | Government Procurement", example="Export"),
):
    crop_category = validate(crop_category, VALID_CROP_CATEGORIES, "crop_category") or crop_category
    validate_year(year)
    validate_quarter(quarter)
    market_type = validate(market_type, VALID_MARKET_TYPES, "market_type") or market_type
    filters_applied = {k: v for k, v in {"crop_name": crop_name, "crop_category": crop_category, "year": year, "quarter": quarter, "market_type": market_type}.items() if v is not None}
    cache_key = "crops:seasonal_trend:" + ":".join(f"{k}={v}" for k, v in filters_applied.items())

    async def fetch():
        df = await run_query("SELECT * FROM vw_harvest_full")
        if crop_name:
            df = df[df["crop_name"].str.lower() == crop_name.lower()]
        if crop_category:
            df = df[df["crop_category"] == crop_category]
        if year:
            df = df[df["year"] == year]
        if quarter:
            df = df[df["quarter"] == quarter]
        if market_type:
            df = df[df["market_type"] == market_type]
        if df.empty:
            return []
        trend = (
            df.groupby(["crop_name", "year", "quarter", "season"], as_index=False)
            .agg(
                total_quantity_sold_ton=("quantity_sold_ton", "sum"),
                total_revenue_bdt=("revenue_bdt", "sum"),
                avg_price_per_ton_bdt=("price_per_ton_bdt", "mean"),
                num_harvests=("revenue_bdt", "count"),
            )
        )
        trend["total_quantity_sold_ton"] = trend["total_quantity_sold_ton"].round(2)
        trend["total_revenue_bdt"] = trend["total_revenue_bdt"].round(2)
        trend["avg_price_per_ton_bdt"] = trend["avg_price_per_ton_bdt"].round(2)
        trend = trend.sort_values(["year", "quarter"])
        return trend.to_dict(orient="records")

    result = await cache_get_set(cache_key, fetch, expire=120)
    return {"filters_applied": filters_applied, "trend": result}


@router.get("/quality-breakdown")
async def quality_breakdown(
    crop_id: Optional[int] = Query(None, description="Crop ID from dim_crop table", example=5),
    crop_category: Optional[str] = Query(None, description="Cereal | Vegetable | Fruit | Pulse | Oilseed | Cash Crop | Spice", example="Fruit"),
    year: Optional[int] = Query(None, description="2022 | 2023 | 2024", example=2024, ge=2022, le=2024),
    region: Optional[str] = Query(None, description="Dhaka | Chittagong | Sylhet | Rajshahi | Khulna | Rangpur | Barisal | Mymensingh", example="Chittagong"),
    market_type: Optional[str] = Query(None, description="Local | Wholesale | Export | Retail | Government Procurement", example="Retail"),
    pesticide_residue: Optional[str] = Query(None, description="None | Trace | Low | High", example="Trace"),
):
    crop_category = validate(crop_category, VALID_CROP_CATEGORIES, "crop_category") or crop_category
    validate_year(year)
    region = validate(region, VALID_REGIONS, "region") or region
    market_type = validate(market_type, VALID_MARKET_TYPES, "market_type") or market_type
    pesticide_residue = validate(pesticide_residue, VALID_PESTICIDE_RESIDUES, "pesticide_residue") or pesticide_residue

    df = await run_query("SELECT * FROM vw_harvest_full")
    if crop_id is not None:
        crop_df = await run_query("SELECT * FROM dim_crop")
        crop_row = crop_df[crop_df["crop_id"] == crop_id]
        if crop_row.empty:
            raise HTTPException(status_code=404, detail=f"crop_id={crop_id} not found.")
        df = df[df["crop_name"] == crop_row.iloc[0]["crop_name"]]
    if crop_category:
        df = df[df["crop_category"] == crop_category]
    if year:
        df = df[df["year"] == year]
    if region:
        df = df[df["region"] == region]
    if market_type:
        df = df[df["market_type"] == market_type]
    if pesticide_residue:
        df = df[df["pesticide_residue"] == pesticide_residue]

    filters_applied = {k: v for k, v in {"crop_id": crop_id, "crop_category": crop_category, "year": year, "region": region, "market_type": market_type, "pesticide_residue": pesticide_residue}.items() if v is not None}
    total_records = len(df)
    if total_records == 0:
        empty_grade = {"count": 0, "pct": 0.0, "avg_revenue_bdt": 0}
        empty_residue = {"count": 0, "pct": 0.0}
        return {
            "filters_applied": filters_applied,
            "total_records": 0,
            "grade_distribution": {g: empty_grade for g in ["A", "B", "C", "D"]},
            "pesticide_residue_breakdown": {r: empty_residue for r in ["None", "Trace", "Low", "High"]},
        }

    grade_dist = {}
    for grade in ["A", "B", "C", "D"]:
        subset = df[df["quality_grade"] == grade]
        count = len(subset)
        grade_dist[grade] = {
            "count": count,
            "pct": round(count / total_records * 100, 2),
            "avg_revenue_bdt": round(float(subset["revenue_bdt"].mean()), 2) if count > 0 else 0,
        }

    residue_dist = {}
    for residue in ["None", "Trace", "Low", "High"]:
        count = len(df[df["pesticide_residue"] == residue])
        residue_dist[residue] = {"count": count, "pct": round(count / total_records * 100, 2)}

    return {
        "filters_applied": filters_applied,
        "total_records": total_records,
        "grade_distribution": grade_dist,
        "pesticide_residue_breakdown": residue_dist,
    }
