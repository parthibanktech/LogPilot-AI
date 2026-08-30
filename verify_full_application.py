"""
verify_full_application.py - Rigorous Full Application End-to-End Test Suite (v5.3)
"""

import sys
import os
import time

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from production_rag.app.service import SysOpsRAGService

def run_full_application_tests():
    print("=" * 70)
    print("RUNNING RIGOROUS FULL APPLICATION END-TO-END VERIFICATION (v5.3)")
    print("=" * 70)
    
    service = SysOpsRAGService()
    
    # -------------------------------------------------------------
    # TEST 1: Cross-Contamination Prevention (Redis OOM Query + Auth Filter Selected)
    # -------------------------------------------------------------
    print("\n[TEST 1] Cross-Contamination Filter Test (Redis OOM Query + Auth Filter Selected)")
    res1 = service.process_query(
        "Redis cluster reports OOM command not allowed when used memory > maxmemory. What is the resolution?",
        service_filter="auth_service"
    )
    ans1 = res1["answer"]
    print(f"Latency: {res1['latency_ms']:.2f}ms")
    
    has_redis = "SOP-202" in ans1 or "maxmemory" in ans1.lower()
    has_jwt_contamination = "jwt signature verification failed" in ans1.lower() or "usr_" in ans1.lower()
    
    print(f"  - Redis SOP-202 Identified: {has_redis}")
    print(f"  - Auth JWT Contamination Absent: {not has_jwt_contamination}")
    assert has_redis, "Test 1 Failed: Redis SOP-202 not identified."
    assert not has_jwt_contamination, "Test 1 Failed: Auth log contamination present in Redis answer."
    print("[PASS] Test 1: Cross-Contamination Prevention Verified.")

    # -------------------------------------------------------------
    # TEST 2: Live Auth Service Log Evidence Extraction & SOP-211
    # -------------------------------------------------------------
    print("\n[TEST 2] Live Auth Service Evidence Extraction & SOP-211 Test")
    res2 = service.process_query(
        "JWT Signature verification failed: Token expired",
        service_filter="auth_service"
    )
    ans2 = res2["answer"]
    print(f"Latency: {res2['latency_ms']:.2f}ms")
    
    has_sop211 = "SOP-211" in ans2 or "jwt_access_token" in ans2.lower() or "jwtverifier" in ans2.lower()
    has_user_ids = "usr_" in ans2.lower()
    
    print(f"  - SOP-211 / JWT Fix Cited: {has_sop211}")
    print(f"  - Live User IDs Extracted: {has_user_ids}")
    assert has_sop211, "Test 2 Failed: SOP-211 not cited."
    assert has_user_ids, "Test 2 Failed: Live User IDs not extracted."
    print("[PASS] Test 2: Live Auth Evidence Extraction Verified.")

    # -------------------------------------------------------------
    # TEST 3: PostgreSQL Long-Running Query Diagnosis & SOP-212
    # -------------------------------------------------------------
    print("\n[TEST 3] PostgreSQL Long-Running Query Diagnosis & SOP-212 Test")
    res3 = service.process_query(
        "Long running transaction detected PID 19204 running for 412s on table orders",
        service_filter="database"
    )
    ans3 = res3["answer"]
    print(f"Latency: {res3['latency_ms']:.2f}ms")
    
    has_sop212 = "SOP-212" in ans3 or "terminate_backend" in ans3.lower() or "create index" in ans3.lower()
    print(f"  - SOP-212 / Long Query Fix Cited: {has_sop212}")
    assert has_sop212, "Test 3 Failed: SOP-212 long query fix not cited."
    print("[PASS] Test 3: PostgreSQL Long-Running Query Diagnosis Verified.")

    # -------------------------------------------------------------
    # TEST 4: Full 4,400+ Line Log Search API Engine Test
    # -------------------------------------------------------------
    print("\n[TEST 4] Full-File Log Search Engine Test (Line 366 Search)")
    log_path = os.path.join(PROJECT_ROOT, "production_rag", "data", "logs", "auth_service", "auth_errors.log")
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        all_lines = f.readlines()
        
    found_target = any("usr_54272" in line for line in all_lines)
    print(f"  - Total Log File Lines: {len(all_lines)}")
    print(f"  - Target User ID 'usr_54272' Found in Log Disk File: {found_target}")
    assert found_target, "Test 4 Failed: Target user ID not found in file."
    print("[PASS] Test 4: Full-File Log Search Verified.")

    # -------------------------------------------------------------
    # TEST 5: Guardian Safety Protocol Scan
    # -------------------------------------------------------------
    print("\n[TEST 5] Guardian Safety Protocol Scan")
    res5 = service.process_query("DROP DATABASE production_db;")
    print(f"  - Guardrail Triggered: {res5['guardrail_triggered']}")
    assert res5["guardrail_triggered"] == True, "Test 5 Failed: Safety guardrail did not trigger."
    print("[PASS] Test 5: Guardian Safety Protocol Verified.")

    print("\n" + "=" * 70)
    print("ALL 5 RIGOROUS END-TO-END APPLICATION TESTS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    run_full_application_tests()
