from tests import (
    test_fahrenheit_celsius_converter,
    test_constraint_propagators,
    visualize_fahrenheit_celsius
)
from tms_tests import (
    test_tms_basic,
    test_tms_contradiction,
    test_tms_visualize
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
    test_tms_visualize()
    
    print("\nAll tests completed.")

if __name__ == "__main__":
    # Check if the user wants to run in REPL mode
    if len(sys.argv) > 1 and sys.argv[1].lower() == "repl":
        # Check if visualization should be disabled
        use_visualization = "--no_vis" not in sys.argv
        
        repl = PropNetworkREPL()
        repl.run(use_visualization=use_visualization)
    else:
        # Default to whatever functions placed here
        run_all_tests()
        visualize_fahrenheit_celsius()
