from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
import pandas as pd
import uvicorn

#DB Config 
from app.config import DATABASE_URL as DB_URL
engine = create_engine(DB_URL, pool_pre_ping=True)

ALLOWED_TABLES = {
    "dim_crop", "dim_date", "dim_farm", "dim_input_supply",
    "dim_market", "fact_harvest_sales",
    "vw_harvest_full", "vw_farm_profitability", "vw_revenue_by_crop_year"
}

app = FastAPI(title="AgriDB Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/db-query")
def db_query(
    table: str = Query(..., description="Table or view name"),
    limit: int = Query(100, description="Max rows to return"),
):
    if table not in ALLOWED_TABLES:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Table '{table}' not allowed.")

    df = pd.read_sql(f"SELECT * FROM `{table}` LIMIT {limit}", engine)
    for col in df.select_dtypes(include=["datetime64[ns]", "object"]).columns:
        df[col] = df[col].astype(str).where(df[col].notna(), None)

    df = df.where(pd.notna(df), None)

    return {
        "table": table,
        "total": len(df),
        "columns": list(df.columns),
        "rows": df.to_dict(orient="records"),
    }

@app.get("/")
def root():
    return {"status": "running", "message": "AgriDB bridge server is up!"}

if __name__ == "__main__":
    print("\nAgriDB Bridge Server starting...")
    print("   Open agriculture_explorer.html in your browser\n")
    uvicorn.run(app, host="127.0.0.1", port=8001)
