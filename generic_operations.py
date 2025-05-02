from nothing import NOTHING
from interval import Interval, add_intervals, sub_intervals, mul_intervals, div_intervals, to_interval, EMPTY_INTERVAL
from multipledispatch import dispatch
from tms import TMS
from layers import make_layered_procedure, base_layer_value, support_layer_value, LayeredDatum
from merge import merge

###----------------------------GENERIC OPERATIONS----------------------------###

# Base operations for each arithmetic function
###----------------------------ADDITION BASE----------------------------###
@dispatch(Interval, Interval)
def _add_base(x, y):
    """Base addition for two intervals."""
    return add_intervals(x, y)

@dispatch(int, int)
@dispatch(float, float)
@dispatch(int, float)
@dispatch(float, int)
def _add_base(x, y):
    """Base addition for two numbers."""
    return x + y

@dispatch(Interval, (int, float))
def _add_base(x, y):
    """Base addition for an interval and a number."""
    return add_intervals(x, to_interval(y))

@dispatch((int, float), Interval)
def _add_base(x, y):
    """Base addition for a number and an interval."""
    return add_intervals(to_interval(x), y)

@dispatch(object, object)
def _add_base(x, y):
    """Default case for addition."""
    # Try using Python's built-in addition
    try:
        return x + y
    except (TypeError, ValueError):
        return NOTHING

###----------------------------SUBTRACTION BASE----------------------------###
@dispatch(Interval, Interval)
def _subtract_base(x, y):
    """Base subtraction for two intervals."""
    return sub_intervals(x, y)

@dispatch(int, int)
@dispatch(float, float)
@dispatch(int, float)
@dispatch(float, int)
def _subtract_base(x, y):
    """Base subtraction for two numbers."""
    return x - y

@dispatch(Interval, (int, float))
def _subtract_base(x, y):
    """Base subtraction for an interval and a number."""
    return sub_intervals(x, to_interval(y))

@dispatch((int, float), Interval)
def _subtract_base(x, y):
    """Base subtraction for a number and an interval."""
    return sub_intervals(to_interval(x), y)

@dispatch(object, object)
def _subtract_base(x, y):
    """Default case for subtraction."""
    # Try using Python's built-in subtraction
    try:
        return x - y
    except (TypeError, ValueError):
        return NOTHING

###----------------------------MULTIPLICATION BASE----------------------------###
@dispatch(Interval, Interval)
def _multiply_base(x, y):
    """Base multiplication for two intervals."""
    return mul_intervals(x, y)

@dispatch(int, int)
@dispatch(float, float)
@dispatch(int, float)
@dispatch(float, int)
def _multiply_base(x, y):
    """Base multiplication for two numbers."""
    return x * y

@dispatch(Interval, (int, float))
def _multiply_base(x, y):
    """Base multiplication for an interval and a number."""
    return mul_intervals(x, to_interval(y))

@dispatch((int, float), Interval)
def _multiply_base(x, y):
    """Base multiplication for a number and an interval."""
    return mul_intervals(to_interval(x), y)

@dispatch(object, object)
def _multiply_base(x, y):
    """Default case for multiplication."""
    # Try using Python's built-in multiplication
    try:
        return x * y
    except (TypeError, ValueError):
        return NOTHING

###----------------------------DIVISION BASE----------------------------###
@dispatch(Interval, Interval)
def _divide_base(x, y):
    """Base division for two intervals."""
    return div_intervals(x, y)

@dispatch((int, float), int)
@dispatch((int, float), float)
def _divide_base(x, y):
    """Base division for two numbers."""
    if y == 0:
        return NOTHING
    return x / y

@dispatch(Interval, (int, float))
def _divide_base(x, y):
    """Base division for an interval and a number."""
    if y == 0:
        return NOTHING
    return div_intervals(x, to_interval(y))

@dispatch((int, float), Interval)
def _divide_base(x, y):
    """Base division for a number and an interval."""
    return div_intervals(to_interval(x), y)

@dispatch(object, object)
def _divide_base(x, y):
    """Default case for division."""
    # Try using Python's built-in division
    try:
        return x / y
    except (TypeError, ValueError, ZeroDivisionError):
        return NOTHING

###----------------------------LAYERED PROCEDURES----------------------------###

# Create layered procedures for each operation
generic_add = make_layered_procedure('add', 2, _add_base)
generic_subtract = make_layered_procedure('subtract', 2, _subtract_base)
generic_multiply = make_layered_procedure('multiply', 2, _multiply_base)
generic_divide = make_layered_procedure('divide', 2, _divide_base)

###----------------------------PARTIAL INFORMATION HANDLING----------------------------###

def generic_unpack(value, continuation):
    """
    Extracts the base content from a value and applies a function to it.
    
    Args:
        value: The value to unpack (could be layered, TMS, etc.)
        continuation: Function to apply to the unpacked value
        
    Returns:
        The result of applying the continuation function to the unpacked value
    """
    # Handle NOTHING specially
    if value is NOTHING:
        return NOTHING
    
    # Handle TMS values (collections of supported values)
    if isinstance(value, TMS):
        # For TMS, we query it to get the strongest consequence
        from tms import tms_query
        return tms_query(value)
    
    # Handle layered data
    if isinstance(value, LayeredDatum):
        # Extract the base value
        base_value = base_layer_value(value)
        
        # Apply the continuation to the base value
        result = continuation(base_value)
        
        # If the result is NOTHING, return NOTHING
        if result is NOTHING:
            return NOTHING
        
        # Apply support information if present
        if value.has_layer('support'):
            support = value.get_layer_value('support')
            return LayeredDatum(result, support=support)
        
        return result
    
    # For regular values, just apply the continuation
    return continuation(value)

def generic_flatten(value):
    """
    Flatten any nested partial information structures.
    
    Args:
        value: Value to flatten (might contain nested layers)
        
    Returns:
        A flattened value with no nested layers
    """
    # Handle NOTHING specially
    if value is NOTHING:
        return NOTHING
    
    # Handle TMS values
    if isinstance(value, TMS):
        # TMS flattening would go here
        return value
    
    # Handle layered data
    if isinstance(value, LayeredDatum):
        # Get the base value
        base = base_layer_value(value)
        
        # If the base is also layered, flatten recursively
        if isinstance(base, LayeredDatum):
            # Use recursive flattening
            from tms import generic_flatten as tms_flatten
            return tms_flatten(value)
        
        return value
    
    # For regular values, return as is
    return value

def generic_bind(value, continuation):
    """
    Handles unpacking a value, applying a function, and flattening the result.
    
    This is the core function for handling partial information in the system.
    
    Args:
        value: Value to process (could be any type with partial information)
        continuation: Function to apply to the unpacked value
        
    Returns:
        The flattened result of applying the continuation to the unpacked value
    """
    # Apply the unpack-apply-flatten sequence
    result = generic_unpack(value, continuation)
    return generic_flatten(result)

def nary_unpacking(function):
    """
    Creates a function that properly handles partial information in its arguments.
    
    Args:
        function: The base function to wrap
        
    Returns:
        A function that handles partial information in its arguments
    """
    def wrapped(*args):
        # Process arguments recursively
        def loop(remaining_args, current_function):
            if not remaining_args:
                return current_function()
            
            # Process the first argument using generic_bind
            return generic_bind(
                remaining_args[0],
                lambda arg: loop(
                    remaining_args[1:],
                    lambda *rest_args: current_function(arg, *rest_args)
                )
            )
        
        return loop(args, function)
    
    # Preserve the function name for debugging
    if hasattr(function, '__name__'):
        wrapped.__name__ = function.__name__
    
    return wrapped

###----------------------------MERGE----------------------------###

@dispatch(object, object)
def generic_merge(content, increment):
    """Generic merge implementation delegating to merge module."""
    return merge(content, increment)

###----------------------------IMPLIED OPERATIONS----------------------------###

def implies(v1, v2):
    """
    Check if v1 implies v2 (v1 is more specific than or equal to v2).
    
    This is true if v1 merged with v2 equals v2.
    """
    merged = merge(v1, v2)
    return merged == v2
