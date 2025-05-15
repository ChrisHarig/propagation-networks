"""Tests for the Truth Maintenance System (TMS) functionality."""

from cell import make_cell
from tms import make_premise, supported_value, kick_out, bring_in, premise_in, tms_query
from example_networks import sum_constraint

def test_tms_basic():
    """Test basic TMS functionality."""
    # Create cells and premises
    a = make_cell("A")
    b = make_cell("B")
    c = make_cell("C")
    
    p1 = make_premise("P1")
    p2 = make_premise("P2")
    
    # Set up sum constraint: A + B = C
    sum_constraint(a, b, c)
    
    # Add values with support
    a.add_content(supported_value(5, [p1]))
    b.add_content(supported_value(10, [p2]))
    
    # Check that C has the correct value and support
    c_content = c.content()
    assert c_content.base == 15
    support_premises = c_content.support.premises
    expected_premises = {p1, p2}
    assert support_premises == expected_premises

def test_tms_contradiction():
    """Test TMS handling of contradictions."""
    # Create cells and premises
    a = make_cell("A")
    b = make_cell("B")
    c = make_cell("C")
    
    p1 = make_premise("P1")
    p2 = make_premise("P2")
    p3 = make_premise("P3")
    
    # Set up sum constraint: A + B = C
    sum_constraint(a, b, c)
    
    # Add initial values
    a.add_content(supported_value(5, [p1]))
    b.add_content(supported_value(10, [p2]))
    
    # Check initial state
    c_content = c.content()
    assert c_content.base == 15
    
    # Try to add a contradictory value
    try:
        c.add_content(supported_value(20, [p3]))
        assert False, "Contradiction not detected"
    except ValueError:
        pass
    
    # Verify the original value is preserved
    c_content = c.content()
    assert c_content.base == 15

def test_tms_worldview():
    """Test TMS worldview management."""
    # Create cells and premises
    a = make_cell("A")
    b = make_cell("B")
    c = make_cell("C")
    
    p1 = make_premise("P1")
    p2 = make_premise("P2")
    
    # Set up sum constraint: A + B = C
    sum_constraint(a, b, c)
    
    # Add values with support
    a.add_content(supported_value(5, [p1]))
    b.add_content(supported_value(10, [p2]))
    
    # Check with both premises in worldview
    assert tms_query(a.content()).base == 5
    assert tms_query(b.content()).base == 10
    assert tms_query(c.content()).base == 15
    
    # Remove P1 from worldview
    kick_out(p1)
    
    # Check with only P2 in worldview
    assert tms_query(a.content()) is None
    assert tms_query(b.content()).base == 10
    assert tms_query(c.content()) is None
    
    # Restore P1 to worldview
    bring_in(p1)
    
    # Check with both premises in worldview again
    assert tms_query(a.content()).base == 5
    assert tms_query(b.content()).base == 10
    assert tms_query(c.content()).base == 15

def test_tms_temperature_converter():
    """Test TMS with the temperature converter example."""
    from example_networks import fahrenheit_celsius_converter
    
    # Create cells and premises
    fahrenheit = make_cell("F")
    celsius = make_cell("C")
    
    thermometer1 = make_premise("Thermometer1")
    thermometer2 = make_premise("Thermometer2")
    
    # Set up the converter
    fahrenheit_celsius_converter(fahrenheit, celsius)
    
    # Add values with support
    fahrenheit.add_content(supported_value(32, [thermometer1]))
    celsius.add_content(supported_value(0, [thermometer2]))
    
    # Check with both thermometers in worldview
    assert tms_query(fahrenheit.content()).base == 32
    assert tms_query(celsius.content()).base == 0

if __name__ == "__main__":
    test_tms_basic()
    test_tms_contradiction()
    test_tms_worldview()
    test_tms_temperature_converter() 