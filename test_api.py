"""
Test script for the Unicorn HAT API.
Run this to test the API endpoints locally.
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test the health endpoint."""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_clear():
    """Test clearing the grid."""
    print("\n=== Testing Clear Endpoint ===")
    response = requests.post(f"{BASE_URL}/clear")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_single_pixel():
    """Test setting a single pixel."""
    print("\n=== Testing Single Pixel Endpoint ===")
    data = {
        "x": 4,
        "y": 4,
        "color": {"r": 255, "g": 0, "b": 0}
    }
    response = requests.post(f"{BASE_URL}/pixel", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_brightness():
    """Test setting brightness."""
    print("\n=== Testing Brightness Endpoint ===")
    data = {"brightness": 0.3}
    response = requests.post(f"{BASE_URL}/brightness", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_full_grid():
    """Test setting the full grid."""
    print("\n=== Testing Full Grid Endpoint ===")
    
    # Create a rainbow pattern
    grid = []
    colors = [
        {"r": 255, "g": 0, "b": 0},      # Red
        {"r": 255, "g": 127, "b": 0},    # Orange
        {"r": 255, "g": 255, "b": 0},    # Yellow
        {"r": 0, "g": 255, "b": 0},      # Green
        {"r": 0, "g": 0, "b": 255},      # Blue
        {"r": 75, "g": 0, "b": 130},     # Indigo
        {"r": 148, "g": 0, "b": 211},    # Violet
        {"r": 255, "g": 255, "b": 255},  # White
    ]
    
    for y in range(8):
        row = []
        for x in range(8):
            row.append(colors[y])
        grid.append(row)
    
    data = {"grid": grid}
    response = requests.post(f"{BASE_URL}/grid", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_invalid_requests():
    """Test error handling with invalid requests."""
    print("\n=== Testing Invalid Requests ===")
    
    # Invalid grid size
    print("\nTest: Invalid grid size")
    data = {"grid": [[{"r": 0, "g": 0, "b": 0}]]}
    response = requests.post(f"{BASE_URL}/grid", json=data)
    print(f"Status: {response.status_code} (expected 400)")
    
    # Invalid color value
    print("\nTest: Invalid color value")
    data = {"x": 0, "y": 0, "color": {"r": 300, "g": 0, "b": 0}}
    response = requests.post(f"{BASE_URL}/pixel", json=data)
    print(f"Status: {response.status_code} (expected 400)")
    
    # Invalid coordinates
    print("\nTest: Invalid coordinates")
    data = {"x": 10, "y": 0, "color": {"r": 255, "g": 0, "b": 0}}
    response = requests.post(f"{BASE_URL}/pixel", json=data)
    print(f"Status: {response.status_code} (expected 400)")
    
    return True

def main():
    print("=" * 50)
    print("Unicorn HAT API Test Suite")
    print("=" * 50)
    print(f"Testing against: {BASE_URL}")
    
    tests = [
        ("Health Check", test_health),
        ("Clear Grid", test_clear),
        ("Single Pixel", test_single_pixel),
        ("Brightness", test_brightness),
        ("Full Grid", test_full_grid),
        ("Invalid Requests", test_invalid_requests),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except requests.exceptions.ConnectionError:
            print(f"\nERROR: Could not connect to {BASE_URL}")
            print("Make sure the server is running: python app.py")
            return
        except Exception as e:
            print(f"\nERROR in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("Test Results")
    print("=" * 50)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

if __name__ == "__main__":
    main()
