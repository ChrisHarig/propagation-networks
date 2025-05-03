from nothing import NOTHING, THE_CONTRADICTION, contradictory, Nothing
from interval import Interval, add_intervals, sub_intervals, mul_intervals, div_intervals, to_interval, EMPTY_INTERVAL
from multipledispatch import dispatch
from layers import make_layered_procedure, base_layer_value, support_layer_value, LayeredDatum

###----------------------------ADDITION BASE----------------------------###

@dispatch(Nothing, object)
@dispatch(object, Nothing)
@dispatch(Nothing, Nothing)
def _add_base(x, y):
    """Base addition for a NOTHING and an object."""
    return NOTHING

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

@dispatch(Nothing, object)
@dispatch(object, Nothing)
@dispatch(Nothing, Nothing)
def _subtract_base(x, y):
    """Base subtraction when one operand is NOTHING."""
    return NOTHING

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

@dispatch(Nothing, object)
@dispatch(object, Nothing)
@dispatch(Nothing, Nothing)
def _multiply_base(x, y):
    """Base multiplication when one operand is NOTHING."""
    return NOTHING

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

@dispatch(Nothing, object)
@dispatch(object, Nothing)
@dispatch(Nothing, Nothing)
def _divide_base(x, y):
    """Base division when one operand is NOTHING."""
    return NOTHING

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

###----------------------------MERGE BASE----------------------------###

@dispatch(object, object)
def _merge_base(content, increment):
    """Default implementation for types without a specific handler."""
    if content == increment:
        return content
    else:
        return THE_CONTRADICTION

@dispatch(Nothing, object)
def _merge_base(content, increment):
    """Handle merging NOTHING with any object."""
    return increment

@dispatch(object, Nothing)
def _merge_base(content, increment):
    """Handle merging any object with NOTHING."""
    return content

@dispatch(Nothing, Nothing)
def _merge_base(content, increment):
    """Handle merging NOTHING with NOTHING."""
    return NOTHING

@dispatch(Interval, Interval)
def _merge_base(content, increment):
    """Merge two intervals by finding their intersection."""
    # Use the intersection of the two intervals
    new_interval = Interval.intersect(content, increment)
    if new_interval.is_empty():
        return THE_CONTRADICTION
    
    # Check if the result is exactly one of the inputs
    tolerance = 1e-9
    if (abs(new_interval.low - content.low) < tolerance and 
        abs(new_interval.high - content.high) < tolerance):
        return content
    if (abs(new_interval.low - increment.low) < tolerance and 
        abs(new_interval.high - increment.high) < tolerance):
        return increment
    
    return new_interval

@dispatch(Interval, (int, float))
def _merge_base(content, increment):
    """Merge an interval with a number."""
    if content.low <= increment <= content.high:
        # The number is consistent with the interval
        return increment
    else:
        # The number is outside the interval - contradiction
        return THE_CONTRADICTION

@dispatch((int, float), Interval)
def _merge_base(content, increment):
    """Merge a number with an interval."""
    if increment.low <= content <= increment.high:
        # The number is consistent with the interval
        return content
    else:
        # The number is outside the interval - contradiction
        return THE_CONTRADICTION

###----------------------------LAYERED PROCEDURES----------------------------###

# Create layered procedures for each operation
generic_add = make_layered_procedure('add', 2, _add_base)
generic_subtract = make_layered_procedure('subtract', 2, _subtract_base)
generic_multiply = make_layered_procedure('multiply', 2, _multiply_base)
generic_divide = make_layered_procedure('divide', 2, _divide_base)
generic_merge = make_layered_procedure('merge', 2, _merge_base)

###----------------------------PUBLIC FUNCTIONS----------------------------###

def implies(v1, v2):
    """
    Check if v1 implies v2 (v1 is more specific than or equal to v2).
    
    This is true if v1 merged with v2 equals v2.
    """
    return generic_merge(v1, v2) == v2


