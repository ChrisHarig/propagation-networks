"""Tests for the basic propagation network functionality."""

from cell import make_cell
from interval import Interval
from example_networks import fahrenheit_celsius_converter, sum_constraint, product_constraint
from graph_visualizer import GraphVisualizer

def test_fahrenheit_celsius_converter():
    """Test the Fahrenheit-Celsius converter with various inputs."""
    print("\n=== Testing Fahrenheit-Celsius Converter ===")

    # Test 1: Set Fahrenheit, check Celsius
    print("\n--- Test 1: F = 212 ---")
    f1 = make_cell("F1")
    c1 = make_cell("C1")
    fahrenheit_celsius_converter(f1, c1)
    f1.add_content(212)
    print(f"F: {f1.content()} (Expected: 212)")
    print(f"C: {c1.content()} (Expected: 100)")

    # Test 2: Set Celsius, check Fahrenheit
    print("\n--- Test 2: C = 0 ---")
    f2 = make_cell("F2")
    c2 = make_cell("C2")
    fahrenheit_celsius_converter(f2, c2)
    c2.add_content(0)
    print(f"C: {c2.content()} (Expected: 0)")
    print(f"F: {f2.content()} (Expected: 32)")

    # Test 3: Set Celsius to an interval, check Fahrenheit interval
    print("\n--- Test 3: C = [10, 20] ---")
    f3 = make_cell("F3")
    c3 = make_cell("C3")
    fahrenheit_celsius_converter(f3, c3)
    c3.add_content(Interval(10, 20))
    print(f"C: {c3.content()} (Expected: Interval([10, 20]))")
    print(f"F: {f3.content()} (Expected: Interval([50, 68]))")

def test_constraint_propagators():
    """Test the constraint propagators with simple values."""
    print("\n=== Testing Constraint Propagators ===")
    
    # Test sum constraint
    print("\n--- Testing Sum Constraint ---")
    a = make_cell("A")
    b = make_cell("B")
    c = make_cell("C")
    sum_constraint(a, b, c)
    
    a.add_content(5)
    b.add_content(10)
    print(f"A: {a.content()} (Expected: 5)")
    print(f"B: {b.content()} (Expected: 10)")
    print(f"C: {c.content()} (Expected: 15)")
    
    # Test bidirectional propagation
    print("\n--- Testing Bidirectional Propagation ---")
    x = make_cell("X")
    y = make_cell("Y")
    z = make_cell("Z")
    sum_constraint(x, y, z)
    
    z.add_content(20)
    x.add_content(8)
    print(f"Z: {z.content()} (Expected: 20)")
    print(f"X: {x.content()} (Expected: 8)")
    print(f"Y: {y.content()} (Expected: 12)")
    
    # Test product constraint
    print("\n--- Testing Product Constraint ---")
    p = make_cell("P")
    q = make_cell("Q")
    r = make_cell("R")
    product_constraint(p, q, r)
    
    p.add_content(6)
    q.add_content(7)
    print(f"P: {p.content()} (Expected: 6)")
    print(f"Q: {q.content()} (Expected: 7)")
    print(f"R: {r.content()} (Expected: 42)")

def test_contradiction_handling():
    """Test how the system handles contradictions."""
    print("\n=== Testing Contradiction Handling ===")
    
    a = make_cell("A")
    b = make_cell("B")
    c = make_cell("C")
    sum_constraint(a, b, c)
    
    print("Setting A=5, B=10")
    a.add_content(5)
    b.add_content(10)
    print(f"C: {c.content()} (Expected: 15)")
    
    print("\nAttempting to set C=20 (should cause contradiction)")
    try:
        c.add_content(20)
        print("✗ Error: Contradiction not detected!")
    except ValueError as e:
        print(f"✓ Correctly caught contradiction: {e}")

def visualize_network():
    """Create and visualize a simple network."""
    print("\n=== Visualizing Network ===")
    
    # Enable visualization
    visualizer = GraphVisualizer()
    import propagator
    import cell
    propagator.set_visualizer(visualizer)
    cell.set_visualizer(visualizer)
    
    # Create a simple temperature converter
    f = make_cell("Fahrenheit")
    c = make_cell("Celsius")
    fahrenheit_celsius_converter(f, c)
    
    # Set a value
    f.add_content(212)
    
    # Display results
    print(f"F: {f.content()} (Expected: 212)")
    print(f"C: {c.content()} (Expected: 100)")
    
    # Draw the network
    visualizer.draw("Temperature Converter")
    
    # Disable visualization
    propagator.set_visualizer(None)
    cell.set_visualizer(None)

def visualize_fahrenheit_celsius():
    """Create and visualize a Fahrenheit-Celsius converter network."""
    print("\n=== Visualizing Fahrenheit-Celsius Converter ===")
    
    # Enable visualization
    visualizer = GraphVisualizer()
    import propagator
    import cell
    propagator.set_visualizer(visualizer)
    cell.set_visualizer(visualizer)
    
    # Create a temperature converter
    f = make_cell("Fahrenheit")
    c = make_cell("Celsius")
    fahrenheit_celsius_converter(f, c)
    
    # Set a value
    f.add_content(212)
    
    # Display results
    print(f"F: {f.content()} (Expected: 212)")
    print(f"C: {c.content()} (Expected: 100)")
    
    # Draw the network
    visualizer.draw("Fahrenheit-Celsius Converter")
    
    # Disable visualization
    propagator.set_visualizer(None)
    cell.set_visualizer(None)

if __name__ == "__main__":
    test_fahrenheit_celsius_converter()
    test_constraint_propagators()
    test_contradiction_handling()
    visualize_network() 