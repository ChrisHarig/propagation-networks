from generic_operations import (
    generic_add, generic_subtract, generic_multiply, generic_divide
)
from cell import make_cell
from propagator import make_propagator, function_to_propagator_constructor

###----------------------------PROPAGATOR CONSTRUCTOR EXAMPLES----------------------------###

def adder():
    """
    Creates a propagator that adds two values.
    
    Usage: adder()(a, b, c) creates a propagator that ensures c = a + b
    """
    return function_to_propagator_constructor(generic_add)

def subtractor():
    """
    Creates a propagator that subtracts one value from another.
    
    Usage: subtractor()(a, b, c) creates a propagator that ensures c = a - b
    """
    return function_to_propagator_constructor(generic_subtract)

def multiplier():
    """
    Creates a propagator that multiplies two values.
    
    Usage: multiplier()(a, b, c) creates a propagator that ensures c = a * b
    """
    return function_to_propagator_constructor(generic_multiply)

def divider():
    """
    Creates a propagator that divides one value by another.
    
    Usage: divider()(a, b, c) creates a propagator that ensures c = a / b
    """
    return function_to_propagator_constructor(generic_divide)

def constant(value):
    """
    Creates a propagator constructor that outputs a constant value.
    
    Usage: constant(5)(output_cell) creates a propagator that sets output_cell to 5
    """
    def constant_function():
        return value
    
    constant_function.__name__ = f"constant({value})"
    return function_to_propagator_constructor(constant_function)

def switch():
    """
    Creates a propagator that implements a conditional switch.
    
    Usage: switch()(control, input, output) creates a propagator that
    sets output to input if control is true, otherwise output is NOTHING
    """
    from nothing import NOTHING
    
    def switch_function(control, input_value):
        if control:
            return input_value
        return NOTHING
    
    switch_function.__name__ = "switch"
    return function_to_propagator_constructor(switch_function) 