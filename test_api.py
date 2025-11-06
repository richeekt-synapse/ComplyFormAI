"""
Quick API test script to verify backend is working
Run this after starting the backend: python test_api.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

def test_health():
    """Test health check endpoint"""
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("   ✓ Health Check PASSED")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"   ✗ Health Check FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ✗ Health Check FAILED: {e}")
        return False

def test_organizations():
    """Test organizations endpoint"""
    print("\n2. Testing Organizations Endpoint...")
    try:
        response = requests.get(f"{API_URL}/organizations")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Organizations PASSED ({len(data)} organizations found)")
            return True
        else:
            print(f"   ✗ Organizations FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ✗ Organizations FAILED: {e}")
        return False

def test_jurisdictions():
    """Test jurisdictions endpoint"""
    print("\n3. Testing Jurisdictions Endpoint...")
    try:
        response = requests.get(f"{API_URL}/jurisdictions")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Jurisdictions PASSED ({len(data)} jurisdictions found)")
            for j in data:
                print(f"      - {j['name']} ({j['code']}): MBE {j.get('mbe_goal_typical', 'N/A')}%")
            return True
        else:
            print(f"   ✗ Jurisdictions FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ✗ Jurisdictions FAILED: {e}")
        return False

def test_compliance_rules():
    """Test compliance rules endpoint"""
    print("\n4. Testing Compliance Rules Endpoint...")
    try:
        response = requests.get(f"{API_URL}/compliance-rules")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Compliance Rules PASSED ({len(data)} rules found)")
            for rule in data:
                print(f"      - {rule['rule_name']} ({rule['rule_type']}) - Severity: {rule['severity']}")
            return True
        else:
            print(f"   ✗ Compliance Rules FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ✗ Compliance Rules FAILED: {e}")
        return False

def test_directory():
    """Test subcontractor directory endpoint"""
    print("\n5. Testing Subcontractor Directory Endpoint...")
    try:
        response = requests.get(f"{API_URL}/directory")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Directory PASSED ({len(data)} subcontractors found)")
            for sub in data[:3]:  # Show first 3
                certs = sub.get('certifications', {})
                cert_list = [k.upper() for k, v in certs.items() if v]
                print(f"      - {sub['legal_name']} ({', '.join(cert_list) if cert_list else 'No certs'})")
            return True
        else:
            print(f"   ✗ Directory FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ✗ Directory FAILED: {e}")
        return False

def test_opportunities():
    """Test opportunities endpoint"""
    print("\n6. Testing Opportunities Endpoint...")
    try:
        response = requests.get(f"{API_URL}/opportunities")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Opportunities PASSED ({len(data)} opportunities found)")
            for opp in data[:3]:  # Show first 3
                print(f"      - {opp['title']}")
                total_value = float(opp.get('total_value', 0)) if opp.get('total_value') else 0
                print(f"        {opp['solicitation_number']} - ${total_value:,.0f}")
            return True
        else:
            print(f"   ✗ Opportunities FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ✗ Opportunities FAILED: {e}")
        return False

def test_create_bid():
    """Test creating a bid"""
    print("\n7. Testing Create Bid Endpoint...")
    try:
        # First get an organization
        orgs_response = requests.get(f"{API_URL}/organizations")
        if orgs_response.status_code != 200 or not orgs_response.json():
            print("   ⚠ Skipping (no organizations available)")
            return True
        
        org_id = orgs_response.json()[0]['id']
        
        # Create a test bid
        bid_data = {
            "organization_id": org_id,
            "solicitation_number": "TEST-001",
            "total_amount": 1000000.00,
            "mbe_goal": 29.0
        }
        
        response = requests.post(f"{API_URL}/bids/", json=bid_data)
        if response.status_code == 201:
            print("   ✓ Create Bid PASSED")
            bid = response.json()
            print(f"      Created bid ID: {bid['id']}")
            
            # Clean up - delete the test bid
            # Note: You may need to implement a delete endpoint
            return True
        else:
            print(f"   ✗ Create Bid FAILED (Status: {response.status_code})")
            print(f"      Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ✗ Create Bid FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("ComplyFormAI API Test Suite")
    print("=" * 70)
    print("\nMake sure the backend is running:")
    print("  uvicorn app.main:app --reload")
    print("\nRunning tests...")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Organizations", test_organizations()))
    results.append(("Jurisdictions", test_jurisdictions()))
    results.append(("Compliance Rules", test_compliance_rules()))
    results.append(("Directory", test_directory()))
    results.append(("Opportunities", test_opportunities()))
    results.append(("Create Bid", test_create_bid()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:8} - {test_name}")
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)
    
    if passed == total:
        print("\n✓ All tests passed! Your API is working correctly.")
        print("\nNext steps:")
        print("  1. Start frontend: npm start")
        print("  2. Open browser: http://localhost:3000")
    else:
        print("\n⚠ Some tests failed. Please check:")
        print("  1. Is the backend running? (uvicorn app.main:app --reload)")
        print("  2. Did you run init_db.py? (python init_db.py)")
        print("  3. Is PostgreSQL running?")
        print("  4. Check backend logs for errors")

if __name__ == "__main__":
    main()