"""
tests.test_live_http_api - Live HTTP Server API Verification Suite
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_live_http_endpoints():
    print("=" * 70)
    print(f"TESTING LIVE HTTP API SERVER AT {BASE_URL}")
    print("=" * 70)
    
    # 1. Health Endpoint Test
    print("\n[HTTP 1] GET /api/health")
    try:
        r1 = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"Status Code: {r1.status_code} | Response: {r1.json()}")
        assert r1.status_code == 200 and r1.json().get("status") == "healthy"
        print("[PASS] HTTP 1: Health Endpoint Verified.")
    except Exception as e:
        print(f"[FAIL] HTTP 1: {e}")
        return

    # 2. Log Search API Test
    print("\n[HTTP 2] GET /api/logs?service=auth_service&search=usr_54272")
    try:
        r2 = requests.get(f"{BASE_URL}/api/logs?service=auth_service&search=usr_54272", timeout=5)
        found = "usr_54272" in r2.json().get("logs", "")
        print(f"Found 'usr_54272' in Search Response: {found}")
        assert found
        print("[PASS] HTTP 2: Log Search Endpoint Verified.")
    except Exception as e:
        print(f"[FAIL] HTTP 2: {e}")

    # 3. Live Query API Test: Auth Error Diagnosis
    print("\n[HTTP 3] POST /api/query (Auth Service JWT Diagnosis)")
    try:
        payload3 = {"query": "JWT Signature verification failed: Token expired", "service_filter": "auth_service"}
        t0 = time.time()
        r3 = requests.post(f"{BASE_URL}/api/query", json=payload3, timeout=25)
        latency = (time.time() - t0) * 1000
        ans3 = r3.json().get("answer", "")
        has_sop211 = "SOP-211" in ans3 or "jwt" in ans3.lower()
        print(f"Status Code: {r3.status_code} | Latency: {latency:.0f}ms | SOP-211 Cited: {has_sop211}")
        assert r3.status_code == 200 and has_sop211
        print("[PASS] HTTP 3: Auth Query Endpoint Verified.")
    except Exception as e:
        print(f"[FAIL] HTTP 3: {e}")

    # 4. Live Query API Test: Redis OOM Query with Auth Filter Selected
    print("\n[HTTP 4] POST /api/query (Redis OOM + Auth Filter Selected - Cross Contamination Check)")
    try:
        payload4 = {"query": "Redis cluster reports OOM command not allowed when used memory > maxmemory. What is the resolution?", "service_filter": "auth_service"}
        t0 = time.time()
        r4 = requests.post(f"{BASE_URL}/api/query", json=payload4, timeout=25)
        latency = (time.time() - t0) * 1000
        ans4 = r4.json().get("answer", "")
        has_sop202 = "SOP-202" in ans4 or "maxmemory" in ans4.lower()
        has_jwt_contam = "jwt signature verification failed" in ans4.lower()
        print(f"Status Code: {r4.status_code} | Latency: {latency:.0f}ms | Redis SOP-202 Cited: {has_sop202} | Zero Auth Contamination: {not has_jwt_contam}")
        assert r4.status_code == 200 and has_sop202 and not has_jwt_contam
        print("[PASS] HTTP 4: Cross-Contamination Prevention Verified.")
    except Exception as e:
        print(f"[FAIL] HTTP 4: {e}")

    # 5. Telemetry Endpoint Test
    print("\n[HTTP 5] GET /api/telemetry")
    try:
        r5 = requests.get(f"{BASE_URL}/api/telemetry", timeout=5)
        print(f"Status Code: {r5.status_code} | Telemetry Summary: {r5.json()}")
        assert r5.status_code == 200
        print("[PASS] HTTP 5: Telemetry Endpoint Verified.")
    except Exception as e:
        print(f"[FAIL] HTTP 5: {e}")

    print("\n" + "=" * 70)
    print("LIVE HTTP API SERVER VALIDATION COMPLETE!")
    print("=" * 70)

if __name__ == "__main__":
    test_live_http_endpoints()
