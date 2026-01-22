"""
Test Runner Script for HRM Decision System

Provides convenient commands to run different test suites.
Usage: python run_tests.py [test_type]
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def run_command(cmd, description):
    """Run a pytest command"""
    print_header(description)
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def run_all_tests():
    """Run all tests"""
    return run_command(
        ["pytest", "-v", "--tb=short"],
        "RUNNING ALL TESTS"
    )


def run_unit_tests():
    """Run unit tests only"""
    return run_command(
        ["pytest", "test_phase1.py", "-v"],
        "RUNNING UNIT TESTS"
    )


def run_integration_tests():
    """Run integration tests"""
    return run_command(
        ["pytest", "test_system.py", "-v"],
        "RUNNING INTEGRATION TESTS"
    )


def run_api_tests():
    """Run API tests"""
    return run_command(
        ["pytest", "test_api.py", "-v"],
        "RUNNING API TESTS"
    )


def run_functional_tests():
    """Run functional tests"""
    return run_command(
        ["pytest", "test_functional.py", "-v"],
        "RUNNING FUNCTIONAL TESTS"
    )


def run_performance_tests():
    """Run performance tests"""
    return run_command(
        ["pytest", "test_performance.py", "-v", "-m", "not slow"],
        "RUNNING PERFORMANCE TESTS (excluding slow tests)"
    )


def run_quick_tests():
    """Run quick smoke tests"""
    return run_command(
        ["pytest", "-k", "test_root_endpoint or test_basic", "-v"],
        "RUNNING QUICK SMOKE TESTS"
    )


def run_with_coverage():
    """Run tests with coverage report"""
    return run_command(
        ["pytest", "--cov=app", "--cov-report=html", "--cov-report=term", "-v"],
        "RUNNING TESTS WITH COVERAGE"
    )


def show_help():
    """Show help message"""
    print_header("HRM DECISION SYSTEM - TEST RUNNER")
    
    print("Available test suites:\n")
    print("  all          - Run all tests")
    print("  unit         - Run unit tests (test_phase1.py)")
    print("  integration  - Run integration tests (test_system.py)")
    print("  api          - Run API endpoint tests (test_api.py)")
    print("  functional   - Run functional/business logic tests")
    print("  performance  - Run performance tests")
    print("  quick        - Run quick smoke tests")
    print("  coverage     - Run tests with coverage report")
    print("\nUsage:")
    print("  python run_tests.py [test_type]")
    print("\nExamples:")
    print("  python run_tests.py all")
    print("  python run_tests.py unit")
    print("  python run_tests.py api")
    print("\n")


def main():
    """Main test runner"""
    
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help", "help"]:
        show_help()
        return 0
    
    test_type = sys.argv[1].lower()
    
    test_runners = {
        "all": run_all_tests,
        "unit": run_unit_tests,
        "integration": run_integration_tests,
        "api": run_api_tests,
        "functional": run_functional_tests,
        "performance": run_performance_tests,
        "quick": run_quick_tests,
        "coverage": run_with_coverage,
    }
    
    if test_type not in test_runners:
        print(f"❌ Unknown test type: {test_type}")
        print("Run 'python run_tests.py help' for available options")
        return 1
    
    # Run the selected test suite
    returncode = test_runners[test_type]()
    
    # Print summary
    if returncode == 0:
        print_header("✅ ALL TESTS PASSED!")
    else:
        print_header("❌ SOME TESTS FAILED")
        print("Review the output above for details\n")
    
    return returncode


if __name__ == "__main__":
    sys.exit(main())
