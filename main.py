from tests import (
    test_fahrenheit_celsius_converter,
    test_constraint_propagators
)
from tms_tests import (
    test_tms_basic,
    test_tms_contradiction
)
from network_repl import PropNetworkREPL
import sys

def run_all_tests():
    """Run all tests for the propagator system."""
    print("Running all tests for the propagator system...\n")
    test_fahrenheit_celsius_converter()
    test_constraint_propagators()  # This tests both adder and multiplier propagators
    
    # Run TMS tests
    test_tms_basic()
    test_tms_contradiction()
    
    print("\nAll tests completed.")

if __name__ == "__main__":
    # Check if the user wants to run in REPL mode
    if len(sys.argv) > 1 and sys.argv[1].lower() == "repl":
        repl = PropNetworkREPL()
        repl.run()
    else:
        # Default to running tests
        run_all_tests()
