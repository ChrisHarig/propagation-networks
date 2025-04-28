"""
Merge functionality for the propagation network.

This module contains functions for merging different types of values,
including partial information and truth maintenance system values.
"""

from nothing import NOTHING, THE_CONTRADICTION, contradictory
from multipledispatch import dispatch
from interval import Interval
from tms import TMS, tms_merge, is_v_and_s

###----------------------------MERGE LOGIC----------------------------###

# Base merge function that delegates to the appropriate implementation
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
    # Special case for NOTHING - handle outside of dispatch system
    if content is NOTHING or increment is NOTHING:
        return increment if content is NOTHING else content
    
    # Use the dispatch system for other cases
    return _merge_dispatch(content, increment)

# Multiple dispatch implementations for different type combinations
@dispatch(object, object)
def _merge_dispatch(content, increment):
    """Default implementation for types without a specific handler."""
    if content == increment:
        return content
    else:
        return THE_CONTRADICTION

@dispatch(Interval, Interval)
def _merge_dispatch(content, increment):
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
def _merge_dispatch(content, increment):
    """Merge an interval with a number."""
    if content.low <= increment <= content.high:
        # The number is consistent with the interval
        return increment
    else:
        # The number is outside the interval - contradiction
        return THE_CONTRADICTION

@dispatch((int, float), Interval)
def _merge_dispatch(content, increment):
    """Merge a number with an interval."""
    if increment.low <= content <= increment.high:
        # The number is consistent with the interval
        return content
    else:
        # The number is outside the interval - contradiction
        return THE_CONTRADICTION

# Handle ValueWithSupport objects
from tms import ValueWithSupport

@dispatch(ValueWithSupport, ValueWithSupport)
def _merge_dispatch(content, increment):
    """Merge two ValueWithSupport objects."""
    return v_and_s_merge(content, increment)

@dispatch(ValueWithSupport, object)
def _merge_dispatch(content, increment):
    """Merge a ValueWithSupport with a regular value."""
    # Wrap the increment in a ValueWithSupport with empty support
    from tms import Support
    increment_vs = ValueWithSupport(increment, Support())
    return v_and_s_merge(content, increment_vs)

@dispatch(object, ValueWithSupport)
def _merge_dispatch(content, increment):
    """Merge a regular value with a ValueWithSupport."""
    # Wrap the content in a ValueWithSupport with empty support
    from tms import Support
    content_vs = ValueWithSupport(content, Support())
    return v_and_s_merge(content_vs, increment)

# TMS-related merge functions

def merge_supports(v_and_s1, v_and_s2):
    """Merge the supports from two v&s structures."""
    return v_and_s1.support.union(v_and_s2.support)

def v_and_s_merge(v_and_s1, v_and_s2):
    """
    Merge two values with support according to the algorithm in the paper.
    
    There are three cases:
    1. If the merged value equals v_and_s1.value (the first value is more specific):
       a. If v_and_s2.value implies the merged value (confirmation), use the more informative support
       b. Otherwise, new information is not interesting, use v_and_s1
    2. If the merged value equals v_and_s2.value (second value is more specific):
       Use v_and_s2 (new information overrides old)
    3. Otherwise (interesting merge with new information), use both supports
    """
    # Import at function level to avoid circular imports
    from tms import supported, implies, more_informative_support
    
    v1 = v_and_s1.value
    v2 = v_and_s2.value
    
    # Merge the values
    merged_value = merge(v1, v2)
    
    # Case 1: Merged value equals v1
    if merged_value == v1:
        if implies(v2, merged_value):
            # 1a: Confirmation of existing information - use more informative support
            if more_informative_support(v_and_s2, v_and_s1):
                return v_and_s2
            return v_and_s1
        # 1b: New information is not interesting
        return v_and_s1
    
    # Case 2: Merged value equals v2 - new information overrides old
    if merged_value == v2:
        return v_and_s2
    
    # Case 3: Interesting merge with new information - need both supports
    return supported(merged_value, merge_supports(v_and_s1, v_and_s2))

# Add dispatch handlers for TMS objects
@dispatch(TMS, TMS)
def _merge_dispatch(content, increment):
    """Merge two TMS objects."""
    return tms_merge(content, increment)

@dispatch(TMS, object)
def _merge_dispatch(content, increment):
    """Merge a TMS with a regular value."""
    # Convert the increment to a TMS
    from tms import supported_value, make_tms
    if is_v_and_s(increment):
        increment_tms = make_tms([increment])
    else:
        # Wrap in a ValueWithSupport with empty support
        increment_tms = make_tms([supported_value(increment, [])])
    return tms_merge(content, increment_tms)

@dispatch(object, TMS)
def _merge_dispatch(content, increment):
    """Merge a regular value with a TMS."""
    # Convert the content to a TMS
    from tms import supported_value, make_tms
    if is_v_and_s(content):
        content_tms = make_tms([content])
    else:
        # Wrap in a ValueWithSupport with empty support
        content_tms = make_tms([supported_value(content, [])])
    return tms_merge(content_tms, increment) 