"""
Support handlers for the layered data system.

This module contains handlers for processing support information
in different operations like addition, multiplication, etc.
"""

from layers import base_layer_value, support_layer_value
from tms import Support, merge_supports

def support_handler_add(base_value, *args):
    """
    Support handler for addition.
    
    For addition, if any value is zero, its support is irrelevant.
    Otherwise, combine supports from all inputs.
    """
    # Get base values and supports
    base_values = [base_layer_value(arg) for arg in args]
    supports = [support_layer_value(arg) or Support() for arg in args]
    
    # If any value is zero, its support is irrelevant
    non_zero_supports = [s for v, s in zip(base_values, supports) if v != 0]
    
    if not non_zero_supports:
        # All values are zero, use the first support
        return supports[0]
    
    # Combine supports from non-zero values
    result = non_zero_supports[0]
    for support in non_zero_supports[1:]:
        result = merge_supports(result, support)
    return result

def support_handler_subtract(base_value, *args):
    """
    Support handler for subtraction.
    
    Similar to addition, but with special handling for zero values.
    """
    # For now, handle the same as addition
    return support_handler_add(base_value, *args)

def support_handler_multiply(base_value, *args):
    """
    Support handler for multiplication.
    
    If any value is zero, the result's support comes only from that value.
    Otherwise, combine all supports.
    """
    # Get base values and supports
    base_values = [base_layer_value(arg) for arg in args]
    supports = [support_layer_value(arg) or Support() for arg in args]
    
    # If any value is zero, the result's support comes only from that value
    for i, value in enumerate(base_values):
        if value == 0:
            return supports[i]
    
    # Otherwise, combine all supports
    result = supports[0]
    for support in supports[1:]:
        result = merge_supports(result, support)
    return result

def support_handler_divide(base_value, *args):
    """
    Support handler for division.
    
    The result's support must include the divisor's support (to avoid division by zero).
    If the numerator is zero, the result's support should only come from the numerator.
    """
    # Get base values and supports
    base_values = [base_layer_value(arg) for arg in args]
    supports = [support_layer_value(arg) or Support() for arg in args]
    
    # If numerator is zero, result's support comes only from numerator
    if base_values[0] == 0:
        return supports[0]
    
    # Otherwise, combine all supports (divisor support is critical)
    result = supports[0]
    for support in supports[1:]:
        result = merge_supports(result, support)
    return result

def support_handler_merge(base_value, content, increment):
    """
    Support handler for merge operation.
    
    Follows the logic outlined in the paper for merging supports.
    """
    # Get support values from the arguments
    support1 = support_layer_value(content) or Support()
    support2 = support_layer_value(increment) or Support()
    
    # Get the base values
    v1 = base_layer_value(content)
    v2 = base_layer_value(increment)
    
    # Case 1: Merged value equals v1
    if base_value == v1:
        # Check if v2 implies the merged value
        from generic_operations import implies
        if implies(v2, base_value):
            # 1a: Confirmation of existing information - use more informative support
            if support2.is_subset(support1) and len(support2.premises) < len(support1.premises):
                return support2
            return support1
        # 1b: New information is not interesting
        return support1
    
    # Case 2: Merged value equals v2 - new information overrides old
    if base_value == v2:
        return support2
    
    # Case 3: Interesting merge with new information - need both supports
    return merge_supports(support1, support2)

def get_support_handlers():
    """
    Get a dictionary of all support handlers.
    
    Returns:
        A dictionary mapping operation names to their support handlers
    """
    return {
        'add': support_handler_add,
        'subtract': support_handler_subtract,
        'multiply': support_handler_multiply,
        'divide': support_handler_divide,
        'merge': support_handler_merge
    } 