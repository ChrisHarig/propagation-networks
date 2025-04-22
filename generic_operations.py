from nothing import NOTHING
from interval import Interval, add_intervals, sub_intervals, mul_intervals, div_intervals, to_interval

###----------------------------GENERIC OPERATIONS----------------------------###

# Define generic operations that can handle different types of partial information
def generic_add(x, y):
    """Generic addition operation."""
    # Handle intervals
    if isinstance(x, Interval) and isinstance(y, Interval):
        return add_intervals(x, y)
    # Handle raw numbers
    elif isinstance(x, (int, float)) and isinstance(y, (int, float)):
        return x + y
    # Handle mixed cases by converting to intervals
    elif isinstance(x, Interval) or isinstance(y, Interval):
        if not isinstance(x, Interval):
            x = to_interval(x)
        if not isinstance(y, Interval):
            y = to_interval(y)
        return add_intervals(x, y)
    else:
        raise TypeError(f"Cannot add {type(x)} and {type(y)}")

def generic_subtract(x, y):
    """Generic subtraction operation."""
    # Handle intervals
    if isinstance(x, Interval) and isinstance(y, Interval):
        return sub_intervals(x, y)
    # Handle raw numbers
    elif isinstance(x, (int, float)) and isinstance(y, (int, float)):
        return x - y
    # Handle mixed cases by converting to intervals
    elif isinstance(x, Interval) or isinstance(y, Interval):
        if not isinstance(x, Interval):
            x = to_interval(x)
        if not isinstance(y, Interval):
            y = to_interval(y)
        return sub_intervals(x, y)
    else:
        raise TypeError(f"Cannot subtract {type(x)} and {type(y)}")

def generic_multiply(x, y):
    """Generic multiplication operation."""
    # Handle intervals
    if isinstance(x, Interval) and isinstance(y, Interval):
        return mul_intervals(x, y)
    # Handle raw numbers
    elif isinstance(x, (int, float)) and isinstance(y, (int, float)):
        return x * y
    # Handle mixed cases by converting to intervals
    elif isinstance(x, Interval) or isinstance(y, Interval):
        if not isinstance(x, Interval):
            x = to_interval(x)
        if not isinstance(y, Interval):
            y = to_interval(y)
        return mul_intervals(x, y)
    else:
        raise TypeError(f"Cannot multiply {type(x)} and {type(y)}")

def generic_divide(x, y):
    """Generic division operation."""
    # Handle division by zero
    if isinstance(y, (int, float)) and y == 0: 
        return NOTHING
    # Handle intervals
    if isinstance(x, Interval) and isinstance(y, Interval):
        return div_intervals(x, y)
    # Handle raw numbers
    elif isinstance(x, (int, float)) and isinstance(y, (int, float)):
        return x / y
    # Handle mixed cases by converting to intervals
    elif isinstance(x, Interval) or isinstance(y, Interval):
        if not isinstance(x, Interval):
            x = to_interval(x)
        if not isinstance(y, Interval):
            y = to_interval(y)
        return div_intervals(x, y)
    else:
        raise TypeError(f"Cannot divide {type(x)} and {type(y)}")

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
