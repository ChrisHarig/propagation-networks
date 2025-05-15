"""Tests for the basic propagation network functionality."""

from cell import make_cell
from interval import Interval
from example_networks import fahrenheit_celsius_converter, sum_constraint, product_constraint

def test_fahrenheit_celsius_converter():
    """Test the Fahrenheit-Celsius converter with various inputs."""
    # Test 1: Set Fahrenheit, check Celsius
    f1 = make_cell("F1")
    c1 = make_cell("C1")
    fahrenheit_celsius_converter(f1, c1)
    f1.add_content(212)
    assert f1.content() == 212
    assert c1.content() == 100

    # Test 2: Set Celsius, check Fahrenheit
    f2 = make_cell("F2")
    c2 = make_cell("C2")
    fahrenheit_celsius_converter(f2, c2)
    c2.add_content(0)
    assert c2.content() == 0
    assert f2.content() == 32

    # Test 3: Set Celsius to an interval, check Fahrenheit interval
    f3 = make_cell("F3")
    c3 = make_cell("C3")
    fahrenheit_celsius_converter(f3, c3)
    c3.add_content(Interval(10, 20))
    assert c3.content() == Interval(10, 20)
    assert f3.content() == Interval(50, 68)

def test_constraint_propagators():
    """Test the constraint propagators with simple values."""
    # Test sum constraint
    a = make_cell("A")
    b = make_cell("B")
    c = make_cell("C")
    sum_constraint(a, b, c)
    
    a.add_content(5)
    b.add_content(10)
    assert a.content() == 5
    assert b.content() == 10
    assert c.content() == 15
    
    # Test bidirectional propagation
    x = make_cell("X")
    y = make_cell("Y")
    z = make_cell("Z")
    sum_constraint(x, y, z)
    
    z.add_content(20)
    x.add_content(8)
    assert z.content() == 20
    assert x.content() == 8
    assert y.content() == 12
    
    # Test product constraint
    p = make_cell("P")
    q = make_cell("Q")
    r = make_cell("R")
    product_constraint(p, q, r)
    
    p.add_content(6)
    q.add_content(7)
    assert p.content() == 6
    assert q.content() == 7
    assert r.content() == 42

def test_contradiction_handling():
    """Test how the system handles contradictions."""
    a = make_cell("A")
    b = make_cell("B")
    c = make_cell("C")
    sum_constraint(a, b, c)
    
    a.add_content(5)
    b.add_content(10)
    assert c.content() == 15
    
    try:
        c.add_content(20)
        assert False, "Contradiction not detected!"
    except ValueError:
        pass

if __name__ == "__main__":
    test_fahrenheit_celsius_converter()
    test_constraint_propagators()
    test_contradiction_handling()
