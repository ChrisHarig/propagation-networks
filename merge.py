"""
Merge functionality for the propagation network.

This module contains functions for merging different types of values,
including partial information and layered data.
"""

from nothing import NOTHING, THE_CONTRADICTION, contradictory
from multipledispatch import dispatch
from interval import Interval
from layers import make_layered_procedure, base_layer_value

###----------------------------MERGE LOGIC----------------------------###

# Base merge function that handles the basic types
@dispatch(object, object)
def _merge_base(content, increment):
    """Default implementation for types without a specific handler."""
    if content == increment:
        return content
    else:
        return THE_CONTRADICTION

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

# Create the layered merge function
_layered_merge = make_layered_procedure('merge', 2, _merge_base)

# Public merge function that handles NOTHING specially, and then uses layered merge
def merge(content, increment):
    """
    Generic merge function for combining partial information.
    
    This is the main extension point for different types of partial information.
    The contract is:
    - If increment adds no new information, return content exactly (by identity)
    - If increment contradicts content, return THE_CONTRADICTION
    - If increment supersedes content, return increment exactly
    - Otherwise, return a new merged value
    """
    # Special case for NOTHING 
    if content is NOTHING:
        return increment
    if increment is NOTHING:
        return content
    
    # Use the layered merge for everything else
    return _layered_merge(content, increment) 