from nothing import NOTHING
from interval import Interval, add_intervals, sub_intervals, mul_intervals, div_intervals, to_interval
from multipledispatch import dispatch
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

###----------------------------PARTIAL INFORMATION HANDLING----------------------------###

def generic_bind(value, continuation):
    """
    Binds a value to a continuation function, handling partial information.
    
    Args:
        value: The value to bind (may be partial information)
        continuation: A function to apply to the unpacked value
        
    Returns:
        The result of applying the continuation to the unpacked value
    """
    # For now, we only handle NOTHING and regular values
    if value is NOTHING:
        return NOTHING
    else:
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
