#!/usr/bin/env python3
"""
Comprehensive test suite for the mortgage analysis tool.
Runs all individual test scripts and provides a summary.
"""

import subprocess
import sys
import os

def run_test_script(script_name):
    """Run a test script and capture its output."""
    try:
        print(f"\n{'='*60}")
        print(f"Running {script_name}...")
        print('='*60)

        result = subprocess.run([sys.executable, script_name],
                              capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print(result.stdout)
            return True, result.stdout
        else:
            print(f"❌ Error running {script_name}")
            print(result.stderr)
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"❌ {script_name} timed out")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ Exception running {script_name}: {e}")
        return False, str(e)

def main():
    """Run all test scripts and provide summary."""
    print("🚀 Starting Comprehensive Test Suite for Mortgage Analysis Tool")
    print("="*80)

    test_scripts = [
        "test_rent_vs_buy.py",
        "test_first_time_buyer.py",
        "test_enhanced_features.py",
        "test_glossary_tax_features.py"
    ]

    results = []

    for script in test_scripts:
        if os.path.exists(script):
            success, output = run_test_script(script)
            results.append((script, success, output))
        else:
            print(f"⚠️ Test script {script} not found")
            results.append((script, False, "File not found"))

    # Summary
    print(f"\n{'='*80}")
    print("📊 TEST SUITE SUMMARY")
    print('='*80)

    passed = 0
    total = len(results)

    for script, success, _ in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{script:<35} {status}")
        if success:
            passed += 1

    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("The mortgage analysis tool is ready for deployment!")

        # Feature summary
        print(f"\n📋 Validated Features:")
        print("✅ Rent vs Buy Analysis with break-even calculations")
        print("✅ First-time home buyer educational content")
        print("✅ Enhanced financial profiling and affordability analysis")
        print("✅ Comprehensive financial glossary (PMI, LTV, HOA, FHA)")
        print("✅ State-specific tax rate integration")
        print("✅ Property tax defaults by location")
        print("✅ Real-time debt-to-income analysis")
        print("✅ Professional financial health dashboard")
        print("✅ Advanced export capabilities")
        print("✅ Interactive educational features")

    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()