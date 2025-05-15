from nothing import NOTHING, THE_CONTRADICTION, contradictory, Nothing
from interval import Interval, add_intervals, sub_intervals, mul_intervals, div_intervals, to_interval, EMPTY_INTERVAL
from multipledispatch import dispatch
from layers import make_layered_procedure, base_layer_value, support_layer_value, LayeredDatum

###----------------------------ADDITION BASE----------------------------###

@dispatch(Nothing, object)
def _add_base(x, y):
    return NOTHING

@dispatch(object, Nothing)
def _add_base(x, y):
    return NOTHING

@dispatch(Nothing, Nothing)
def _add_base(x, y):
    return NOTHING

@dispatch(Interval, Interval)
def _add_base(x, y):
    return add_intervals(x, y)

@dispatch(int, int)
def _add_base(x, y):
    return x + y

@dispatch(float, float)
def _add_base(x, y):
    return x + y

@dispatch(int, float)
def _add_base(x, y):
    return x + y

@dispatch(float, int)
def _add_base(x, y):
    return x + y

@dispatch(Interval, (int, float))
def _add_base(x, y):
    return add_intervals(x, to_interval(y))

@dispatch((int, float), Interval)
def _add_base(x, y):
    return add_intervals(to_interval(x), y)

@dispatch(object, object)
def _add_base(x, y):
    if isinstance(x, Nothing) or isinstance(y, Nothing):
        return NOTHING
    try:
        return x + y
    except (TypeError, ValueError):
        return NOTHING

###----------------------------SUBTRACTION BASE----------------------------###

@dispatch(Nothing, object)
def _subtract_base(x, y):
    return NOTHING

@dispatch(object, Nothing)
def _subtract_base(x, y):
    return NOTHING

@dispatch(Nothing, Nothing)
def _subtract_base(x, y):
    return NOTHING

@dispatch(Interval, Interval)
def _subtract_base(x, y):
    return sub_intervals(x, y)

@dispatch(int, int)
def _subtract_base(x, y):
    return x - y

@dispatch(float, float)
def _subtract_base(x, y):
    return x - y

@dispatch(int, float)
def _subtract_base(x, y):
    return x - y

@dispatch(float, int)
def _subtract_base(x, y):
    return x - y

@dispatch(Interval, (int, float))
def _subtract_base(x, y):
    return sub_intervals(x, to_interval(y))

@dispatch((int, float), Interval)
def _subtract_base(x, y):
    return sub_intervals(to_interval(x), y)

@dispatch(object, object)
def _subtract_base(x, y):
    try:
        return x - y
    except (TypeError, ValueError):
        return NOTHING

###----------------------------MULTIPLICATION BASE----------------------------###

@dispatch(Nothing, object)
def _multiply_base(x, y):
    return NOTHING

@dispatch(object, Nothing)
def _multiply_base(x, y):
    return NOTHING

@dispatch(Nothing, Nothing)
def _multiply_base(x, y):
    return NOTHING

@dispatch(Interval, Interval)
def _multiply_base(x, y):
    return mul_intervals(x, y)

@dispatch(int, int)
def _multiply_base(x, y):
    return x * y

@dispatch(float, float)
def _multiply_base(x, y):
    return x * y

@dispatch(int, float)
def _multiply_base(x, y):
    return x * y

@dispatch(float, int)
def _multiply_base(x, y):
    return x * y

@dispatch(Interval, (int, float))
def _multiply_base(x, y):
    return mul_intervals(x, to_interval(y))

@dispatch((int, float), Interval)
def _multiply_base(x, y):
    return mul_intervals(to_interval(x), y)

@dispatch(object, object)
def _multiply_base(x, y):
    try:
        return x * y
    except (TypeError, ValueError):
        return NOTHING

###----------------------------DIVISION BASE----------------------------###

@dispatch(Nothing, object)
def _divide_base(x, y):
    return NOTHING

@dispatch(object, Nothing)
def _divide_base(x, y):
    return NOTHING

@dispatch(Nothing, Nothing)
def _divide_base(x, y):
    return NOTHING

@dispatch(Interval, Interval)
def _divide_base(x, y):
    return div_intervals(x, y)

@dispatch((int, float), int)
def _divide_base(x, y):
    if y == 0:
        return NOTHING
    return x / y

@dispatch((int, float), float)
def _divide_base(x, y):
    if y == 0:
        return NOTHING
    return x / y

@dispatch(Interval, (int, float))
def _divide_base(x, y):
    if y == 0:
        return NOTHING
    return div_intervals(x, to_interval(y))

@dispatch((int, float), Interval)
def _divide_base(x, y):
    return div_intervals(to_interval(x), y)

@dispatch(object, object)
def _divide_base(x, y):
    try:
        return x / y
    except (TypeError, ValueError, ZeroDivisionError):
        return NOTHING

###----------------------------MERGE BASE----------------------------###

@dispatch(object, object)
def _merge_base(content, increment):
    if content == increment:
        return content
    else:
        return THE_CONTRADICTION

@dispatch(Nothing, object)
def _merge_base(content, increment):
    return increment

@dispatch(object, Nothing)
def _merge_base(content, increment):
    return content

@dispatch(Nothing, Nothing)
def _merge_base(content, increment):
    return NOTHING

@dispatch(Interval, Interval)
def _merge_base(content, increment):
    new_interval = Interval.intersect(content, increment)
    if new_interval.is_empty():
        return THE_CONTRADICTION
    
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
    if content.low <= increment <= content.high:
        return increment
    else:
        return THE_CONTRADICTION

@dispatch((int, float), Interval)
def _merge_base(content, increment):
    if increment.low <= content <= increment.high:
        return content
    else:
        return THE_CONTRADICTION

###----------------------------LAYERED PROCEDURES----------------------------###

generic_add = make_layered_procedure('add', 2, _add_base)
generic_subtract = make_layered_procedure('subtract', 2, _subtract_base)
generic_multiply = make_layered_procedure('multiply', 2, _multiply_base)
generic_divide = make_layered_procedure('divide', 2, _divide_base)
generic_merge = make_layered_procedure('merge', 2, _merge_base)

###----------------------------PUBLIC FUNCTIONS----------------------------###

def implies(v1, v2):
    return generic_merge(v1, v2) == v2


