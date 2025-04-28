from nothing import NOTHING
from interval import Interval, add_intervals, sub_intervals, mul_intervals, div_intervals, to_interval, EMPTY_INTERVAL
from multipledispatch import dispatch
from tms import is_v_and_s, ValueWithSupport, supported, generic_flatten
from merge import merge

###----------------------------GENERIC OPERATIONS----------------------------###

# We use dispatch to handle different arguments

###----------------------------ADDITION----------------------------###
@dispatch(Interval, Interval)
def generic_add(x, y):
    """Generic addition for two intervals."""
    return add_intervals(x, y)

@dispatch(int, int)
@dispatch(float, float)
@dispatch(int, float)
@dispatch(float, int)
def generic_add(x, y):
    """Generic addition for two numbers."""
    return x + y

@dispatch(Interval, (int, float))
def generic_add(x, y):
    """Generic addition for an interval and a number."""
    return add_intervals(x, to_interval(y))

@dispatch((int, float), Interval)
def generic_add(x, y):
    """Generic addition for a number and an interval."""
    return add_intervals(to_interval(x), y)

@dispatch(ValueWithSupport, ValueWithSupport)
def generic_add(x, y):
    """Add two ValueWithSupport objects."""
    result_value = generic_add(x.value, y.value)
    # Combine the supports
    from merge import merge_supports
    result_support = merge_supports(x, y)
    return ValueWithSupport(result_value, result_support)

@dispatch(ValueWithSupport, object)
def generic_add(x, y):
    """Add a ValueWithSupport to a regular value."""
    result_value = generic_add(x.value, y)
    return ValueWithSupport(result_value, x.support)

@dispatch(object, ValueWithSupport)
def generic_add(x, y):
    """Add a regular value to a ValueWithSupport."""
    result_value = generic_add(x, y.value)
    return ValueWithSupport(result_value, y.support)

###----------------------------SUBTRACTION----------------------------###
@dispatch(Interval, Interval)
def generic_subtract(x, y):
    """Generic subtraction for two intervals."""
    return sub_intervals(x, y)

@dispatch(int, int)
@dispatch(float, float)
@dispatch(int, float)
@dispatch(float, int)
def generic_subtract(x, y):
    """Generic subtraction for two numbers."""
    return x - y

@dispatch(Interval, (int, float))
def generic_subtract(x, y):
    """Generic subtraction for an interval and a number."""
    return sub_intervals(x, to_interval(y))

@dispatch((int, float), Interval)
def generic_subtract(x, y):
    """Generic subtraction for a number and an interval."""
    return sub_intervals(to_interval(x), y)

@dispatch(ValueWithSupport, ValueWithSupport)
def generic_subtract(x, y):
    result_value = generic_subtract(x.value, y.value)
    from merge import merge_supports
    result_support = merge_supports(x, y)
    return ValueWithSupport(result_value, result_support)

@dispatch(ValueWithSupport, object)
def generic_subtract(x, y):
    result_value = generic_subtract(x.value, y)
    return ValueWithSupport(result_value, x.support)

@dispatch(object, ValueWithSupport)
def generic_subtract(x, y):
    result_value = generic_subtract(x, y.value)
    return ValueWithSupport(result_value, y.support)

###----------------------------MULTIPLICATION----------------------------###
@dispatch(Interval, Interval)
def generic_multiply(x, y):
    """Generic multiplication for two intervals."""
    return mul_intervals(x, y)

@dispatch(int, int)
@dispatch(float, float)
@dispatch(int, float)
@dispatch(float, int)
def generic_multiply(x, y):
    """Generic multiplication for two numbers."""
    return x * y

@dispatch(Interval, (int, float))
def generic_multiply(x, y):
    """Generic multiplication for an interval and a number."""
    return mul_intervals(x, to_interval(y))

@dispatch((int, float), Interval)
def generic_multiply(x, y):
    """Generic multiplication for a number and an interval."""
    return mul_intervals(to_interval(x), y)

@dispatch(ValueWithSupport, ValueWithSupport)
def generic_multiply(x, y):
    result_value = generic_multiply(x.value, y.value)
    from merge import merge_supports
    result_support = merge_supports(x, y)
    return ValueWithSupport(result_value, result_support)

@dispatch(ValueWithSupport, object)
def generic_multiply(x, y):
    result_value = generic_multiply(x.value, y)
    return ValueWithSupport(result_value, x.support)

@dispatch(object, ValueWithSupport)
def generic_multiply(x, y):
    result_value = generic_multiply(x, y.value)
    return ValueWithSupport(result_value, y.support)

###----------------------------DIVISION----------------------------###
@dispatch(Interval, Interval)
def generic_divide(x, y):
    """Generic division for two intervals."""
    return div_intervals(x, y)

@dispatch((int, float), int)
@dispatch((int, float), float)
def generic_divide(x, y):
    """Generic division for two numbers."""
    if y == 0:
        return NOTHING
    return x / y

@dispatch(Interval, (int, float))
def generic_divide(x, y):
    """Generic division for an interval and a number."""
    if y == 0:
        return NOTHING
    return div_intervals(x, to_interval(y))

@dispatch((int, float), Interval)
def generic_divide(x, y):
    """Generic division for a number and an interval."""
    return div_intervals(to_interval(x), y)

@dispatch(ValueWithSupport, ValueWithSupport)
def generic_divide(x, y):
    result_value = generic_divide(x.value, y.value)
    from merge import merge_supports
    result_support = merge_supports(x, y)
    return ValueWithSupport(result_value, result_support)

@dispatch(ValueWithSupport, object)
def generic_divide(x, y):
    result_value = generic_divide(x.value, y)
    return ValueWithSupport(result_value, x.support)

@dispatch(object, ValueWithSupport)
def generic_divide(x, y):
    result_value = generic_divide(x, y.value)
    return ValueWithSupport(result_value, y.support)

###----------------------------PARTIAL INFORMATION HANDLING----------------------------###

def generic_bind(value, continuation):
    """
    Binds a value to a continuation function, handling partial information and TMS.
    """
    from nothing import NOTHING
    from tms import generic_flatten, is_v_and_s, ValueWithSupport
    
    # Handle NOTHING case first
    if value is NOTHING:
        return NOTHING
    
    # Handle ValueWithSupport
    if is_v_and_s(value):
        # Flatten any nested ValueWithSupport objects
        flattened = generic_flatten(value)
        
        # Extract the actual value, ensuring it's not another ValueWithSupport
        inner_value = flattened.value
        
        # Make sure we're not passing a ValueWithSupport to the continuation
        # This is the key fix to prevent recursion
        while is_v_and_s(inner_value):
            inner_value = inner_value.value
        
        # Apply the continuation to the fully unwrapped inner value
        result = continuation(inner_value)
        
        # If the result is NOTHING, return NOTHING
        if result is NOTHING:
            return NOTHING
        
        # If the result is already a ValueWithSupport, merge the supports
        if is_v_and_s(result):
            from merge import merge_supports
            result_support = merge_supports(flattened, result)
            return ValueWithSupport(result.value, result_support)
        
        # Otherwise, return a new ValueWithSupport with the original support
        return ValueWithSupport(result, flattened.support)
    
    # For regular values, just apply the continuation
    return continuation(value)

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
    """Generic merge implementation delegating to cell.merge."""
    from cell import merge
    return merge(content, increment)
