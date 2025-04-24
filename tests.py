from cell import make_cell
from interval import Interval
from example_networks import fahrenheit_celsius_converter, sum_constraint, product_constraint
from propagator_constructors import adder, multiplier
from graph_visualizer import GraphVisualizer

def visualize_fahrenheit_celsius():
    """Create and visualize a Fahrenheit-Celsius converter network."""
    print("\nCreating and visualizing Fahrenheit-Celsius converter...")
    
    # Create a visualizer
    visualizer = GraphVisualizer()
    
    # Enable visualization globally
    import propagator
    import cell
    propagator.set_visualizer(visualizer)
    cell.set_visualizer(visualizer)
    
    # Create cells for temperature
    fahrenheit = make_cell("F")
    celsius = make_cell("C")
    
    # Set up the converter
    fahrenheit_celsius_converter(fahrenheit, celsius)
    
    # Set a value to demonstrate propagation
    fahrenheit.add_content(212)
    
    # Display results
    print(f"Fahrenheit: {fahrenheit.content()} (Expected: 212)")
    print(f"Celsius: {celsius.content()} (Expected: 100)")
    
    # Draw the network
    visualizer.draw("fahrenheit_celsius_converter")
    
    # Disable visualization
    propagator.set_visualizer(None)
    cell.set_visualizer(None)

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
    print("\n--- Test 5: Testing contradiction handling ---")
    print("Setting C=0, which should make F=32")
    c5.add_content(0)
    print(f"Current state: C={c5.content()} (Expected: 0), F={f5.content()} (Expected: 32)")
    
    print("\nNow attempting to set F=50, which should cause a contradiction")
    try:
        f5.add_content(50) # Contradiction: F cannot be 50 if C is 0
        print(f"ERROR: No contradiction detected! C={c5.content()}, F={f5.content()}")
    except ValueError as e:
        print(f"✓ Correctly caught contradiction: {e}")
        print(f"Final state: C={c5.content()} (Expected: 0), F={f5.content()} (Expected: 32)")

def test_adder_propagator():
    """Test the adder propagator with simple values."""
    print("\nTesting Adder Propagator:")
    
    a = make_cell("A")
    b = make_cell("B")
    c = make_cell("C")

    # Use sum_constraint instead of adder() directly
    sum_constraint(a, b, c)

    a.add_content(5)
    b.add_content(10)
    print(f"A: {a.content()} (Expected: 5), B: {b.content()} (Expected: 10), C: {c.content()} (Expected: 15)")

    # Test contradiction handling
    print("\nTesting contradiction handling:")
    print("Current state: A=5, B=10, C=15")
    print("Attempting to set C=20, which should cause a contradiction")
    try:
        c.add_content(20)  # This should cause a contradiction since c should be 15
        print(f"ERROR: No contradiction detected! A={a.content()}, B={b.content()}, C={c.content()}")
    except ValueError as e:
        print(f"✓ Correctly caught contradiction: {e}")
        print(f"Final state: A={a.content()}, B={b.content()}, C={c.content()}")

    # Test with new cells to avoid previous contradiction
    print("\n--- Testing bidirectional propagation with new cells ---")
    a2 = make_cell("A2")
    b2 = make_cell("B2")
    c2 = make_cell("C2")
    
    # Use sum_constraint instead of adder() directly
    sum_constraint(a2, b2, c2)
    
    # Set c first, then one of the inputs
    print("Setting C=15, then A=7, should compute B=8")
    c2.add_content(15)
    a2.add_content(7)
    print(f"C: {c2.content()} (Expected: 15), A: {a2.content()} (Expected: 7), B: {b2.content()} (Expected: 8)")

def test_multiplier_propagator():
    """Test the multiplier propagator with simple values."""
    print("\nTesting Multiplier Propagator:")
    
    x = make_cell("X")
    y = make_cell("Y")
    total = make_cell("Total")

    # Use product_constraint instead of multiplier() directly
    product_constraint(x, y, total)

    x.add_content(3)
    y.add_content(4)
    print(f"X: {x.content()} (Expected: 3), Y: {y.content()} (Expected: 4), Total: {total.content()} (Expected: 12)")

    # Test contradiction handling
    print("\nTesting contradiction handling:")
    print("Current state: X=3, Y=4, Total=12")
    print("Attempting to set Total=24, which should cause a contradiction")
    try:
        total.add_content(24)  # This should cause a contradiction since total should be 12
        print(f"ERROR: No contradiction detected! X={x.content()}, Y={y.content()}, Total={total.content()}")
    except ValueError as e:
        print(f"✓ Correctly caught contradiction: {e}")
        print(f"Final state: X={x.content()}, Y={y.content()}, Total={total.content()}")

    # Test with new cells to avoid previous contradiction
    print("\n--- Testing bidirectional propagation with new cells ---")
    x2 = make_cell("X2")
    y2 = make_cell("Y2")
    total2 = make_cell("Total2")
    
    # Use product_constraint instead of multiplier() directly
    product_constraint(x2, y2, total2)
    
    # Set total first, then one of the inputs
    print("Setting Total=24, then X=6, should compute Y=4")
    total2.add_content(24)
    x2.add_content(6)
    print(f"Total: {total2.content()} (Expected: 24), X: {x2.content()} (Expected: 6), Y: {y2.content()} (Expected: 4)")

if __name__ == "__main__":
    test_fahrenheit_celsius_converter()
    test_adder_propagator()
    test_multiplier_propagator()
    visualize_fahrenheit_celsius() 