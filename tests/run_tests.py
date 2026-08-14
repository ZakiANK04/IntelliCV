#!/usr/bin/env python
"""
IntelliCV Test Runner
Comprehensive test execution with detailed reporting.
"""
import sys
import os
import unittest
import argparse
from datetime import datetime
from io import StringIO

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ColoredTestResult(unittest.TestResult):
    """Custom test result with colored output"""
    
    # ANSI color codes
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.verbosity = verbosity
        self.successes = []
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes.append(test)
        if self.verbosity > 1:
            self.stream.write(f"{self.GREEN}✓{self.RESET} {test}\n")
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity > 1:
            self.stream.write(f"{self.RED}✗ ERROR{self.RESET} {test}\n")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity > 1:
            self.stream.write(f"{self.RED}✗ FAIL{self.RESET} {test}\n")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.verbosity > 1:
            self.stream.write(f"{self.YELLOW}⊘ SKIP{self.RESET} {test}: {reason}\n")


class ColoredTestRunner(unittest.TextTestRunner):
    """Custom test runner with colored output"""
    
    resultclass = ColoredTestResult
    
    def __init__(self, **kwargs):
        kwargs['verbosity'] = kwargs.get('verbosity', 2)
        super().__init__(**kwargs)


def print_header():
    """Print test runner header"""
    print("\n" + "="*80)
    print("  🧪 INTELLICV TEST SUITE")
    print("  NLP-Powered Resume Intelligence Platform")
    print("="*80)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")


def print_summary(result, duration):
    """Print test summary"""
    total = result.testsRun
    passed = len(result.successes) if hasattr(result, 'successes') else total - len(result.failures) - len(result.errors)
    failed = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    
    print("\n" + "="*80)
    print("  📊 TEST SUMMARY")
    print("="*80)
    print(f"  Total Tests:  {total}")
    print(f"  ✅ Passed:    {passed}")
    print(f"  ❌ Failed:    {failed}")
    print(f"  💥 Errors:    {errors}")
    print(f"  ⊘ Skipped:    {skipped}")
    print(f"  ⏱️ Duration:   {duration:.2f}s")
    print("-"*80)
    
    if total > 0:
        pass_rate = passed / total * 100
        status = "✅ ALL TESTS PASSED" if failed == 0 and errors == 0 else "❌ SOME TESTS FAILED"
        print(f"  Pass Rate: {pass_rate:.1f}%")
        print(f"  Status: {status}")
    
    print("="*80 + "\n")
    
    # Print failures and errors if any
    if result.failures:
        print("\n❌ FAILURES:")
        print("-"*80)
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)
    
    if result.errors:
        print("\n💥 ERRORS:")
        print("-"*80)
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)


def discover_and_run_tests(test_pattern='test_*.py', start_dir=None):
    """Discover and run all tests"""
    if start_dir is None:
        start_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir, pattern=test_pattern)
    
    # Run tests
    runner = ColoredTestRunner(verbosity=2)
    
    import time
    start_time = time.time()
    result = runner.run(suite)
    duration = time.time() - start_time
    
    return result, duration


def run_specific_tests(test_modules):
    """Run specific test modules"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            suite.addTests(loader.loadTestsFromModule(module))
        except ImportError as e:
            print(f"Warning: Could not import {module_name}: {e}")
    
    runner = ColoredTestRunner(verbosity=2)
    
    import time
    start_time = time.time()
    result = runner.run(suite)
    duration = time.time() - start_time
    
    return result, duration


def run_quick_tests():
    """Run quick validation tests only"""
    from tests.test_nlp_analyzer import TestNLPAnalyzerInitialization, TestScoring
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestNLPAnalyzerInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestScoring))
    
    runner = ColoredTestRunner(verbosity=2)
    
    import time
    start_time = time.time()
    result = runner.run(suite)
    duration = time.time() - start_time
    
    return result, duration


def run_accuracy_validation():
    """Run accuracy validation"""
    from tests.accuracy_validator import run_validation
    return run_validation()


def main():
    parser = argparse.ArgumentParser(description='IntelliCV Test Runner')
    parser.add_argument('--quick', '-q', action='store_true', 
                       help='Run quick tests only')
    parser.add_argument('--accuracy', '-a', action='store_true',
                       help='Run accuracy validation only')
    parser.add_argument('--unit', '-u', action='store_true',
                       help='Run unit tests only')
    parser.add_argument('--integration', '-i', action='store_true',
                       help='Run integration tests only')
    parser.add_argument('--all', action='store_true',
                       help='Run all tests including accuracy validation')
    parser.add_argument('--module', '-m', type=str, nargs='+',
                       help='Run specific test module(s)')
    
    args = parser.parse_args()
    
    print_header()
    
    if args.accuracy:
        print("🎯 Running Accuracy Validation...\n")
        run_accuracy_validation()
        return
    
    if args.quick:
        print("⚡ Running Quick Tests...\n")
        result, duration = run_quick_tests()
        print_summary(result, duration)
        return result.wasSuccessful()
    
    if args.module:
        print(f"📦 Running Specific Modules: {args.module}\n")
        result, duration = run_specific_tests(args.module)
        print_summary(result, duration)
        return result.wasSuccessful()
    
    if args.unit:
        print("🔬 Running Unit Tests...\n")
        result, duration = discover_and_run_tests(test_pattern='test_nlp*.py')
        print_summary(result, duration)
        return result.wasSuccessful()
    
    if args.integration:
        print("🔗 Running Integration Tests...\n")
        result, duration = discover_and_run_tests(test_pattern='test_integration*.py')
        print_summary(result, duration)
        return result.wasSuccessful()
    
    # Default: run all unit and integration tests
    print("🧪 Running All Tests...\n")
    result, duration = discover_and_run_tests()
    print_summary(result, duration)
    
    if args.all:
        print("\n🎯 Running Accuracy Validation...\n")
        run_accuracy_validation()
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
