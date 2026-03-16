#!/usr/bin/env python3
"""Test all backend API endpoints"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def test_endpoints():
    print("=== Testing Backend API Endpoints ===\n")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Health check
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✓ GET /api/health: {resp.status_code}")
            print(f"  → Status: {data.get('status')}, Active threads: {data.get('active_threads')}\n")
            tests_passed += 1
        else:
            print(f"✗ GET /api/health: {resp.status_code}\n")
            tests_failed += 1
    except Exception as e:
        print(f"✗ GET /api/health: {e}\n")
        tests_failed += 1
    
    # Test 2: Campaign list
    try:
        resp = requests.get(f"{API_BASE}/campaigns", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✓ GET /api/campaigns: {resp.status_code}")
            print(f"  → Found {len(data)} campaigns")
            if data:
                print(f"  → Latest: {data[0].get('brief')[:50]}... (ID: {data[0].get('id')})\n")
            else:
                print("  → No campaigns yet\n")
            tests_passed += 1
        else:
            print(f"✗ GET /api/campaigns: {resp.status_code}\n")
            tests_failed += 1
    except Exception as e:
        print(f"✗ GET /api/campaigns: {e}\n")
        tests_failed += 1
    
    # Test 3: Analytics trends
    try:
        resp = requests.get(f"{API_BASE}/analytics/trends", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✓ GET /api/analytics/trends: {resp.status_code}")
            print(f"  → Total campaigns: {data.get('total_campaigns')}")
            print(f"  → Total EO: {data.get('total_eo')}, Total EC: {data.get('total_ec')}")
            print(f"  → Avg open rate: {data.get('avg_open_rate'):.2%}, Avg click rate: {data.get('avg_click_rate'):.2%}\n")
            tests_passed += 1
        else:
            print(f"✗ GET /api/analytics/trends: {resp.status_code}\n")
            tests_failed += 1
    except Exception as e:
        print(f"✗ GET /api/analytics/trends: {e}\n")
        tests_failed += 1
    
    # Test 4: Start campaign (with sample brief)
    try:
        payload = {"brief": "Test campaign brief for Acme Corp product launch"}
        resp = requests.post(
            f"{API_BASE}/campaign/start",
            json=payload,
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            print(f"✓ POST /api/campaign/start: {resp.status_code}")
            print(f"  → Thread ID: {data.get('thread_id')}")
            print(f"  → Campaign ID: {data.get('campaign_id')}")
            print(f"  → Status: {data.get('status')}\n")
            tests_passed += 1
            
            # Save thread_id for further testing
            thread_id = data.get('thread_id')
            campaign_id = data.get('campaign_id')
            
            # Test 5: Get campaign status
            try:
                resp = requests.get(f"{API_BASE}/campaign/status/{thread_id}", timeout=5)
                if resp.status_code == 200:
                    status_data = resp.json()
                    print(f"✓ GET /api/campaign/status/{{thread_id}}: {resp.status_code}")
                    print(f"  → Status: {status_data.get('status')}")
                    print(f"  → Campaign phase from state: {status_data.get('state', {}).get('status')}\n")
                    tests_passed += 1
                else:
                    print(f"✗ GET /api/campaign/status/{{thread_id}}: {resp.status_code}\n")
                    tests_failed += 1
            except Exception as e:
                print(f"✗ GET /api/campaign/status/{{thread_id}}: {e}\n")
                tests_failed += 1
            
            # Test 6: Get campaign events
            try:
                resp = requests.get(f"{API_BASE}/campaign/{campaign_id}/events", timeout=5)
                if resp.status_code == 200:
                    events = resp.json()
                    print(f"✓ GET /api/campaign/{{id}}/events: {resp.status_code}")
                    print(f"  → Found {len(events)} events")
                    if events:
                        print(f"  → Latest: {events[-1].get('action')} at {events[-1].get('timestamp')}\n")
                    else:
                        print("  → No events yet\n")
                    tests_passed += 1
                else:
                    print(f"✗ GET /api/campaign/{{id}}/events: {resp.status_code}\n")
                    tests_failed += 1
            except Exception as e:
                print(f"✗ GET /api/campaign/{{id}}/events: {e}\n")
                tests_failed += 1
            
            # Test 7: Get approval history
            try:
                resp = requests.get(f"{API_BASE}/campaign/{campaign_id}/approvals", timeout=5)
                if resp.status_code == 200:
                    approvals = resp.json()
                    print(f"✓ GET /api/campaign/{{id}}/approvals: {resp.status_code}")
                    print(f"  → Found {len(approvals)} approvals\n")
                    tests_passed += 1
                else:
                    print(f"✗ GET /api/campaign/{{id}}/approvals: {resp.status_code}\n")
                    tests_failed += 1
            except Exception as e:
                print(f"✗ GET /api/campaign/{{id}}/approvals: {e}\n")
                tests_failed += 1
            
            # Test 8: Get iterations
            try:
                resp = requests.get(f"{API_BASE}/campaign/{campaign_id}/iterations", timeout=5)
                if resp.status_code == 200:
                    iterations = resp.json()
                    print(f"✓ GET /api/campaign/{{id}}/iterations: {resp.status_code}")
                    print(f"  → Found {len(iterations)} iterations\n")
                    tests_passed += 1
                else:
                    print(f"✗ GET /api/campaign/{{id}}/iterations: {resp.status_code}\n")
                    tests_failed += 1
            except Exception as e:
                print(f"✗ GET /api/campaign/{{id}}/iterations: {e}\n")
                tests_failed += 1
        else:
            print(f"✗ POST /api/campaign/start: {resp.status_code}\n")
            tests_failed += 1
    except Exception as e:
        print(f"✗ POST /api/campaign/start: {e}\n")
        tests_failed += 1
    
    print(f"\n=== Results ===")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    print(f"Total: {tests_passed + tests_failed}")
    
    return tests_failed == 0

if __name__ == "__main__":
    success = test_endpoints()
    exit(0 if success else 1)
