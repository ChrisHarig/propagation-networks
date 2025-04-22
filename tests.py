from cell import make_cell
from interval import Interval
from example_networks import fahrenheit_celsius_converter
from propagator_constructors import adder, multiplier

def test_fahrenheit_celsius_converter():
    """Test the Fahrenheit-Celsius converter with various inputs."""
    print("Testing Fahrenheit-Celsius converter with Intervals:")

    # Create cells for temperature
    fahrenheit = make_cell("F")
    celsius = make_cell("C")

    # Set up the converter
    fahrenheit_celsius_converter(fahrenheit, celsius)

    # Test 1: Set Fahrenheit, check Celsius
    print("\n--- Test 1: F = 212 ---")
    fahrenheit.add_content(212)
    print(f"Fahrenheit: {fahrenheit.content()} (Expected: 212)")
    print(f"Celsius: {celsius.content()} (Expected: 100)")

    # Create new cells for the next test
    f2 = make_cell("F2")
    c2 = make_cell("C2")
    fahrenheit_celsius_converter(f2, c2)

    # Test 2: Set Celsius, check Fahrenheit
    print("\n--- Test 2: C = 0 ---")
    c2.add_content(0)
    print(f"Celsius: {c2.content()} (Expected: 0)")
    print(f"Fahrenheit: {f2.content()} (Expected: 32)")

    # Create new cells for interval test
    f3 = make_cell("F3")
    c3 = make_cell("C3")
    fahrenheit_celsius_converter(f3, c3)

    # Test 3: Set Celsius to an interval, check Fahrenheit interval
    print("\n--- Test 3: C = [10, 20] ---")
    c3.add_content(Interval(10, 20))
    print(f"Celsius: {c3.content()} (Expected: Interval([10, 20]))")
    print(f"Fahrenheit: {f3.content()} (Expected: Interval([50, 68]))")

    # Create new cells for interval test
    f4 = make_cell("F4")
    c4 = make_cell("C4")
    fahrenheit_celsius_converter(f4, c4)

    # Test 4: Set Fahrenheit to an interval, check Celsius interval
    print("\n--- Test 4: F = [50, 68] ---")
    f4.add_content(Interval(50, 68))
    print(f"Fahrenheit: {f4.content()} (Expected: Interval([50, 68]))")
    print(f"Celsius: {c4.content()} (Expected: Interval([10, 20]))")

    # Create new cells for contradiction test
    f5 = make_cell("F5")
    c5 = make_cell("C5")
    fahrenheit_celsius_converter(f5, c5)

    # Test 5: Introduce a contradiction
    print("\n--- Test 5: Contradiction ---")
    try:
        c5.add_content(0)  # Should set F5 to 32
        print(f"After C=0: C={c5.content()} (Expected: 0), F={f5.content()} (Expected: 32)")
        f5.add_content(50) # Contradiction: F cannot be 50 if C is 0
        print(f"After F=50: C={c5.content()}, F={f5.content()}") # Should not reach here
    except ValueError as e:
        print(f"Caught expected contradiction: {e}")
        print(f"Final state: C={c5.content()} (Expected: 0), F={f5.content()} (Expected: 32)")

def test_adder_propagator():
    """Test the adder propagator with simple values."""
    print("\nTesting Adder Propagator:")

    a = make_cell("A")
    b = make_cell("B")
    c = make_cell("C")

    adder()(a, b, c)

    a.add_content(5)
    b.add_content(10)
    print(f"A: {a.content()} (Expected: 5), B: {b.content()} (Expected: 10), C: {c.content()} (Expected: 15)")

    c.add_content(20)
    print(f"A: {a.content()} (Expected: 10), B: {b.content()} (Expected: 10), C: {c.content()} (Expected: 20)")

def test_multiplier_propagator():
    """Test the multiplier propagator with simple values."""
    print("\nTesting Multiplier Propagator:")

    x = make_cell("X")
    y = make_cell("Y")
    total = make_cell("Total")

    multiplier()(x, y, total)

    x.add_content(3)
    y.add_content(4)
    print(f"X: {x.content()} (Expected: 3), Y: {y.content()} (Expected: 4), Total: {total.content()} (Expected: 12)")

    total.add_content(24)
    print(f"X: {x.content()} (Expected: 6), Y: {y.content()} (Expected: 4), Total: {total.content()} (Expected: 24)")

if __name__ == "__main__":
    test_fahrenheit_celsius_converter()
    test_adder_propagator()
    test_multiplier_propagator() 