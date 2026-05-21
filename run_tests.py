import sys
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def run_tests():
    print("Starting API Endpoints Verification Suite...\n")
    success = True

    # 1. Test Root
    try:
        print("Testing GET / ...")
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["status"] == "running"
        print("[OK] Root endpoint\n")
    except Exception as e:
        print(f"[FAIL] Root endpoint: {e}\n")
        success = False

    # 2. Test Endpoint 1 - Farm Summary
    try:
        print("Testing GET /farms/summary ...")
        r = client.get("/farms/summary")
        assert r.status_code == 200
        res = r.json()
        assert "total_farms" in res
        assert "data" in res
        assert len(res["data"]) > 0
        
        # Test filters
        print("Testing GET /farms/summary with valid filters ...")
        r = client.get("/farms/summary?region=Dhaka&year=2023")
        assert r.status_code == 200
        res = r.json()
        assert res["filters_applied"]["region"] == "Dhaka"
        assert res["filters_applied"]["year"] == 2023
        
        # Test invalid filters
        print("Testing GET /farms/summary with invalid filter (expect 422) ...")
        r = client.get("/farms/summary?region=InvalidCity")
        assert r.status_code == 422
        
        print("[OK] Farm Summary endpoint\n")
    except Exception as e:
        print(f"[FAIL] Farm Summary endpoint: {e}\n")
        success = False

    # 3. Test Endpoint 2 - Single Farm Performance
    try:
        print("Testing GET /farms/1/performance ...")
        r = client.get("/farms/1/performance")
        assert r.status_code == 200
        res = r.json()
        assert res["farm_id"] == 1
        assert "farm_name" in res
        assert "performance" in res
        
        # Test filters
        print("Testing GET /farms/1/performance with valid filters ...")
        r = client.get("/farms/1/performance?year=2023&crop_category=Cereal")
        assert r.status_code == 200
        res = r.json()
        assert res["filters_applied"]["year"] == 2023
        assert res["filters_applied"]["crop_category"] == "Cereal"

        # Test invalid farm ID
        print("Testing GET /farms/999/performance (expect 404) ...")
        r = client.get("/farms/999/performance")
        assert r.status_code == 404

        print("[OK] Single Farm Performance endpoint\n")
    except Exception as e:
        print(f"[FAIL] Single Farm Performance endpoint: {e}\n")
        success = False

    # 4. Test Endpoint 3 - Top Farms Ranking
    try:
        print("Testing GET /farms/top ...")
        r = client.get("/farms/top")
        assert r.status_code == 200
        res = r.json()
        assert "rankings" in res
        assert len(res["rankings"]) > 0
        
        # Test limit
        print("Testing GET /farms/top with limit=5 ...")
        r = client.get("/farms/top?limit=5")
        assert r.status_code == 200
        res = r.json()
        assert len(res["rankings"]) <= 5
        
        # Test yield metric
        print("Testing GET /farms/top with metric=yield ...")
        r = client.get("/farms/top?metric=yield")
        assert r.status_code == 200
        
        print("[OK] Top Farms Ranking endpoint\n")
    except Exception as e:
        print(f"[FAIL] Top Farms Ranking endpoint: {e}\n")
        success = False

    # 5. Test Endpoint 4 - Loss Analysis
    try:
        print("Testing GET /farms/loss-analysis ...")
        r = client.get("/farms/loss-analysis")
        assert r.status_code == 200
        res = r.json()
        assert "summary" in res
        assert "breakdown" in res
        assert "overall_loss_pct" in res["summary"]
        
        # Test filters
        print("Testing GET /farms/loss-analysis with filters ...")
        r = client.get("/farms/loss-analysis?season=Winter&year=2023")
        assert r.status_code == 200
        
        print("[OK] Loss Analysis endpoint\n")
    except Exception as e:
        print(f"[FAIL] Loss Analysis endpoint: {e}\n")
        success = False

    # 6. Test Endpoint 5 - Crop Yield Efficiency
    try:
        print("Testing GET /crops/yield-efficiency ...")
        r = client.get("/crops/yield-efficiency")
        assert r.status_code == 200
        res = r.json()
        assert "data" in res
        
        # Test filters
        print("Testing GET /crops/yield-efficiency with filters ...")
        r = client.get("/crops/yield-efficiency?crop_category=Cereal&year=2023")
        assert r.status_code == 200
        res = r.json()
        assert res["filters_applied"]["crop_category"] == "Cereal"
        assert res["filters_applied"]["year"] == 2023
        
        print("[OK] Crop Yield Efficiency endpoint\n")
    except Exception as e:
        print(f"[FAIL] Crop Yield Efficiency endpoint: {e}\n")
        success = False

    # 7. Test Endpoint 6 - Seasonal Revenue Trend
    try:
        print("Testing GET /crops/seasonal-trend ...")
        r = client.get("/crops/seasonal-trend")
        assert r.status_code == 200
        res = r.json()
        assert "trend" in res
        
        # Test filters
        print("Testing GET /crops/seasonal-trend with filters ...")
        r = client.get("/crops/seasonal-trend?crop_category=Vegetable&year=2023")
        assert r.status_code == 200
        res = r.json()
        assert res["filters_applied"]["crop_category"] == "Vegetable"
        assert res["filters_applied"]["year"] == 2023
        
        print("[OK] Seasonal Revenue Trend endpoint\n")
    except Exception as e:
        print(f"[FAIL] Seasonal Revenue Trend endpoint: {e}\n")
        success = False

    # 8. Test Endpoint 7 - Market Price Comparison
    try:
        print("Testing GET /markets/price-comparison ...")
        r = client.get("/markets/price-comparison")
        assert r.status_code == 200
        res = r.json()
        assert "comparison" in res
        
        # Test filters
        print("Testing GET /markets/price-comparison with filters ...")
        r = client.get("/markets/price-comparison?market_type=Export&crop_category=Cereal")
        assert r.status_code == 200
        res = r.json()
        assert res["filters_applied"]["market_type"] == "Export"
        assert res["filters_applied"]["crop_category"] == "Cereal"
        
        print("[OK] Market Price Comparison endpoint\n")
    except Exception as e:
        print(f"[FAIL] Market Price Comparison endpoint: {e}\n")
        success = False

    # 9. Test Endpoint 8 - Quality Grade Breakdown
    try:
        print("Testing GET /crops/quality-breakdown ...")
        r = client.get("/crops/quality-breakdown")
        assert r.status_code == 200
        res = r.json()
        assert "grade_distribution" in res
        assert "pesticide_residue_breakdown" in res
        
        # Test filters
        print("Testing GET /crops/quality-breakdown with filters ...")
        r = client.get("/crops/quality-breakdown?crop_category=Fruit&year=2023&region=Rajshahi")
        assert r.status_code == 200
        res = r.json()
        assert res["filters_applied"]["crop_category"] == "Fruit"
        assert res["filters_applied"]["year"] == 2023
        assert res["filters_applied"]["region"] == "Rajshahi"
        
        print("[OK] Quality Grade Breakdown endpoint\n")
    except Exception as e:
        print(f"[FAIL] Quality Grade Breakdown endpoint: {e}\n")
        success = False

    if success:
        print("ALL ENDPOINTS WORKING PERFECTLY!")
        sys.exit(0)
    else:
        print("SOME ENDPOINTS FAILED VERIFICATION.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
