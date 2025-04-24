from tests import (
    test_fahrenheit_celsius_converter,
    test_adder_propagator,
    test_multiplier_propagator,
    visualize_fahrenheit_celsius
)

def run_all_tests():
    """Run all tests for the propagator system."""
    print("Running all tests for the propagator system...\n")
    test_fahrenheit_celsius_converter()
    test_adder_propagator()
    test_multiplier_propagator()
    print("\nAll tests completed.")

if __name__ == "__main__":
    run_all_tests()
    visualize_fahrenheit_celsius()
