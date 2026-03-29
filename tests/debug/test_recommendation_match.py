#!/usr/bin/env python3
"""
Test script for recommendation_match logic.
Verifies that the system correctly identifies when recommended item matches purchased items.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.integrations.supabase_integration import (
    _compute_recommendation_match,
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("TESTING RECOMMENDATION MATCH LOGIC")
print("="*70)

test_cases = [
    {
        "name": "Perfect match: Single item purchased, matches recommendation",
        "recommended": "Chocolate Cake",
        "purchased": [{"name": "Chocolate Cake", "price": 25.00}],
        "expected": "match",
    },
    {
        "name": "No match: Single item purchased, doesn't match",
        "recommended": "Chocolate Cake",
        "purchased": [{"name": "Vanilla Cake", "price": 20.00}],
        "expected": "did_not_match",
    },
    {
        "name": "Match in multi-item purchase: Recommendation is one of many",
        "recommended": "Chocolate Cake",
        "purchased": [
            {"name": "Vanilla Cake", "price": 20.00},
            {"name": "Chocolate Cake", "price": 25.00},
            {"name": "Strawberry Cake", "price": 22.00},
        ],
        "expected": "match",
    },
    {
        "name": "No match in multi-item purchase: Recommendation not purchased",
        "recommended": "Carrot Cake",
        "purchased": [
            {"name": "Vanilla Cake", "price": 20.00},
            {"name": "Chocolate Cake", "price": 25.00},
        ],
        "expected": "did_not_match",
    },
    {
        "name": "Case insensitive: Different case",
        "recommended": "CHOCOLATE CAKE",
        "purchased": [{"name": "chocolate cake", "price": 25.00}],
        "expected": "match",
    },
    {
        "name": "Whitespace handling: Extra spaces",
        "recommended": "  Chocolate Cake  ",
        "purchased": [{"name": "Chocolate Cake", "price": 25.00}],
        "expected": "match",
    },
    {
        "name": "Missing recommendation: 'unknown' value",
        "recommended": "unknown",
        "purchased": [{"name": "Chocolate Cake", "price": 25.00}],
        "expected": "unknown",
    },
    {
        "name": "Empty purchased list",
        "recommended": "Chocolate Cake",
        "purchased": [],
        "expected": "unknown",
    },
    {
        "name": "None purchased list",
        "recommended": "Chocolate Cake",
        "purchased": None,
        "expected": "unknown",
    },
    {
        "name": "List of strings instead of dicts",
        "recommended": "Chocolate Cake",
        "purchased": ["Vanilla Cake", "Chocolate Cake", "Strawberry Cake"],
        "expected": "match",
    },
    {
        "name": "Empty string recommendation",
        "recommended": "",
        "purchased": [{"name": "Chocolate Cake", "price": 25.00}],
        "expected": "unknown",
    },
    {
        "name": "None recommendation",
        "recommended": None,
        "purchased": [{"name": "Chocolate Cake", "price": 25.00}],
        "expected": "unknown",
    },
]

passed = 0
failed = 0

for i, test_case in enumerate(test_cases, 1):
    print(f"\n{i}️⃣  Test: {test_case['name']}")
    
    result = _compute_recommendation_match(
        recommended_cake=test_case["recommended"],
        purchased_items=test_case["purchased"],
    )
    
    expected = test_case["expected"]
    
    if result == expected:
        print(f"   ✅ PASS")
        print(f"   Recommended: '{test_case['recommended']}'")
        print(f"   Purchased: {test_case['purchased']}")
        print(f"   Result: '{result}'")
        passed += 1
    else:
        print(f"   ❌ FAIL")
        print(f"   Recommended: '{test_case['recommended']}'")
        print(f"   Purchased: {test_case['purchased']}")
        print(f"   Expected: '{expected}', Got: '{result}'")
        failed += 1

print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print(f"✅ Passed: {passed}/{len(test_cases)}")
print(f"❌ Failed: {failed}/{len(test_cases)}")

if failed == 0:
    print("\n✨ ALL TESTS PASSED! Recommendation match logic is working correctly.")
    sys.exit(0)
else:
    print(f"\n⚠️  {failed} test(s) failed. Please review the logic.")
    sys.exit(1)
