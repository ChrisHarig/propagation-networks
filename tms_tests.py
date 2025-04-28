"""Tests for the Truth Maintenance System implementation."""

from cell import make_cell
from tms import make_premise, supported_value, kick_out, bring_in, tms_query
from example_networks import fahrenheit_celsius_converter, sum_constraint

def test_tms_basic():
    """Basic test of the TMS functionality."""
    print("\n=== Testing Basic TMS Functionality ===")
    
    # Create cells and set up a sum constraint
    a = make_cell("A")
    b = make_cell("B")
    c = make_cell("C")
    sum_constraint(a, b, c)
    
    # Create premises and add supported values
    p1 = make_premise("P1")
    p2 = make_premise("P2")
    
    print("Adding A=5 supported by P1")
    a.add_content(supported_value(5, [p1]))
    
    print("Adding B=10 supported by P2")
    b.add_content(supported_value(10, [p2]))
    
    # Check the result
    c_content = c.content()
    print(f"C value: {c_content}")
    
    # Verify support contains both premises
    support_premises = {str(p) for p in c_content.support.premises}
    expected_premises = {"P1", "P2"}
    if support_premises == expected_premises:
        print("✓ Support is correct")
    else:
        print(f"✗ Support is incorrect. Expected {expected_premises}, got {support_premises}")

def test_tms_contradiction():
    """Test how TMS handles contradictions."""
    print("\n=== Testing TMS with Contradictions ===")
    
    # Create cells and set up a sum constraint
    a = make_cell("A")
    b = make_cell("B")
    c = make_cell("C")
    sum_constraint(a, b, c)
    
    # Create premises and add supported values
    p1 = make_premise("P1")
    p2 = make_premise("P2")
    p3 = make_premise("P3")
    
    print("Adding A=5 supported by P1")
    a.add_content(supported_value(5, [p1]))
    
    print("Adding B=10 supported by P2")
    b.add_content(supported_value(10, [p2]))
    
    # Check the result
    c_content = c.content()
    print(f"C value: {c_content}")
    
    # Try to add a contradictory value
    print("\nAttempting to add contradictory value C=20 supported by P3")
    try:
        c.add_content(supported_value(20, [p3]))
        print("✗ Error: Contradiction not detected")
    except ValueError as e:
        print(f"✓ Correctly caught contradiction: {e}")
    
    # Verify cell content is unchanged
    c_content = c.content()
    print(f"C value after contradiction attempt: {c_content}")

def test_tms_worldview():
    """Test the TMS worldview functionality."""
    print("\n=== Testing TMS Worldview Management ===")
    
    # Create cells and set up a sum constraint
    a = make_cell("A")
    b = make_cell("B")
    c = make_cell("C")
    sum_constraint(a, b, c)
    
    # Create premises and add supported values
    p1 = make_premise("P1")
    p2 = make_premise("P2")
    
    print("Adding A=5 supported by P1")
    a.add_content(supported_value(5, [p1]))
    
    print("Adding B=10 supported by P2")
    b.add_content(supported_value(10, [p2]))
    
    # Check the result with both premises
    print("\nWith both P1 and P2 in worldview:")
    print(f"A: {tms_query(a.content())}")
    print(f"B: {tms_query(b.content())}")
    print(f"C: {tms_query(c.content())}")
    
    # Remove P1 from worldview
    print("\nRemoving P1 from worldview:")
    kick_out("P1")
    
    # Check results with only P2
    print("With only P2 in worldview:")
    print(f"A: {tms_query(a.content())}")
    print(f"B: {tms_query(b.content())}")
    print(f"C: {tms_query(c.content())}")
    
    # Restore P1 to worldview
    print("\nRestoring P1 to worldview:")
    bring_in("P1")
    
    # Check results with both premises again
    print("With both P1 and P2 in worldview:")
    print(f"A: {tms_query(a.content())}")
    print(f"B: {tms_query(b.content())}")
    print(f"C: {tms_query(c.content())}")

def test_tms_temperature_converter():
    """Test TMS with the temperature converter example."""
    print("\n=== Testing TMS with Temperature Converter ===")
    
    # Create cells for temperature
    fahrenheit = make_cell("F")
    celsius = make_cell("C")
    
    # Set up the converter
    fahrenheit_celsius_converter(fahrenheit, celsius)
    
    # Create premises for different temperature measurements
    p1 = make_premise("Thermometer1")
    p2 = make_premise("Thermometer2")
    
    # Add supported values from different thermometers
    print("Adding F=32 supported by Thermometer1")
    fahrenheit.add_content(supported_value(32, [p1]))
    
    print("Adding C=0 supported by Thermometer2")
    celsius.add_content(supported_value(0, [p2]))
    
    # Check results with both premises
    print("\nWith both thermometers in worldview:")
    print(f"F: {tms_query(fahrenheit.content())}")
    print(f"C: {tms_query(celsius.content())}")
    
    # Remove Thermometer1 from worldview
    print("\nRemoving Thermometer1 from worldview:")
    kick_out("Thermometer1")
    
    # Check results with only Thermometer2
    print("With only Thermometer2 in worldview:")
    print(f"F: {tms_query(fahrenheit.content())}")
    print(f"C: {tms_query(celsius.content())}")

if __name__ == "__main__":
    test_tms_basic()
    test_tms_contradiction()
    test_tms_worldview()
    test_tms_temperature_converter() 